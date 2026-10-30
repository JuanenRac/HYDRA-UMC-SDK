# Server claims, jog arming and safety limits

Clients for the routes of HYDRA-UMC-SERVER that decide who controls a robot and how far a jog may go (block 1 of the server contract v2). They exist in the four languages of the SDK, replay the same cases and are additive: a request that sends no `controllerId` is the v1 request, a response field a client does not know is ignored, and an error code it does not know stays a plain error.

The server decides. Limits, claims and arming are checked in the server for every client; these clients only build the request and tell the answers apart. They add nothing to the bridge gate (`evaluate_job`), which is untouched.

## Routes

| Route | Who | Python | TypeScript | Go | Rust |
|---|---|---|---|---|---|
| `POST /api/robot/{id}/claim` | signed-in account | `claim_request`, `ServerClient.claim` | `claimRequest`, `HydraServerClient.claim` | `ClaimRequest`, `ServerClient.Claim` | `claim_request` |
| `POST /api/robot/{id}/release` | holder or admin | `release_request`, `.release` | `releaseRequest`, `.release` | `ReleaseRequest`, `.Release` | `release_request` |
| `POST /api/robot/{id}/jog-arm` | signed-in account | `jog_arm_request`, `.jog_arm` | `jogArmRequest`, `.jogArm` | `JogArmRequest`, `.JogArm` | `jog_arm_request` |
| `GET /api/claims` | signed-in account | `list_claims_request`, `.list_claims` | `listClaimsRequest`, `.listClaims` | `ListClaimsRequest`, `.ListClaims` | `list_claims_request` |
| `GET /api/safety-limits[?robotId=]` | signed-in account | `safety_limits_request`, `.safety_limits` | `safetyLimitsRequest`, `.safetyLimits` | `SafetyLimitsRequest`, `.SafetyLimits` | `safety_limits_request` |
| `PUT /api/admin/safety-limits` | admin | `update_safety_limits_request`, `.update_safety_limits` | `updateSafetyLimitsRequest`, `.updateSafetyLimits` | `UpdateSafetyLimitsRequest`, `.UpdateSafetyLimits` | `update_safety_limits_request` |
| `POST /api/robot/{id}/command` (with `controllerId`) | signed-in account | `command_request`, `.command` | `commandRequest`, `.command` | `CommandRequest`, `.Command` | `command_request` |

Python: `hydra_umc_sdk.server_api` (the main names are also exported from the package root). TypeScript: the package entry point. Go: package `hydraumc`. Rust: `hydra_umc_sdk::server_api`.

Every language has two layers. The request builders and response parsers never touch the network, so any HTTP stack can carry them. Python, TypeScript and Go also ship a thin client (`ServerClient` over `urllib`, `HydraServerClient` over `fetch`, `ServerClient` over `net/http`; each takes an injectable transport) that adds the bearer token and a default controller id. The Rust module has no HTTP client on purpose: it keeps the crate free of a networking dependency.

## The controller id

`controllerId` is chosen by one control client (a window, a tab, a phone) for its session: 1 to 64 characters of letters, digits and `. _ : -`. The builders refuse anything else before sending (`ServerRequestError`; in Go the empty string means "not sent"). The builders put it in the JSON body of `claim`, `release`, `jog-arm` and `command`; the server also accepts it as the `X-Controller-Id` header (`CONTROLLER_ID_HEADER`). The clients take a default controller id once, and a call may pass its own.

A claim belongs to an account and, when a controller id was sent, to that controller. `GET /api/claims` calls the cell of the settings tree `cellId`; its `controllerId` is the client that holds the claim (`null` when the claim has none).

## Errors

Every error answer becomes a typed error that keeps the HTTP status, the readable text, the `code` and the whole body.

| Case | Status | `code` | Python / TypeScript | Go | Rust |
|---|---|---|---|---|---|
| Another account holds the claim | 409 | `other-account` | `ClaimConflictError` | `*ClaimConflictError` | `ApiError::ClaimConflict` |
| Another controller of your account holds it | 409 | `other-controller` | `ClaimConflictError` | `*ClaimConflictError` | `ApiError::ClaimConflict` |
| The claim has a controller and none was sent, or the server demands one to claim | 409 / 400 | `controller-id-required` | `ControllerIdRequiredError` (also a `ClaimConflictError`) | `*ControllerIDRequiredError` | `ApiError::ControllerIdRequired` |
| Malformed controller id | 400 | `invalid-controller-id` | `InvalidControllerIdError` | `*InvalidControllerIDError` | `ApiError::InvalidControllerId` |
| A jog on a robot that is not armed | 403 | `jog-not-armed` | `JogNotArmedError` | `*JogNotArmedError` | `ApiError::JogNotArmed` |
| A 409 with a `reservation` and no code (a server that predates the codes) | 409 | none | `ClaimConflictError` with no code | `*ClaimConflictError` | `ApiError::ClaimConflict` |
| Anything else, including an unknown code | any | kept | `ApiError` | `*APIError` | `ApiError::Other` |

`ClaimConflictError` and `ControllerIdRequiredError` carry the `reservation` that blocks the caller. In Go every typed error unwraps to `*APIError` (`errors.As`, or `AsAPIError`). A `409` on the settings tree (a revision conflict) has no reservation and stays a plain error.

## Jog arming and the safety limits

`jog-arm` arms or disarms the jog of one robot for the account and controller that ask; it only matters while the administrator turned `jog.armRequired` on, in which case a `jog` command without arming is answered `403` (`jog-not-armed`). `stop`, the global stop and `release` clear the arming. The answer carries `armed` and, when armed, `expiresAt` and `ttlMs`.

`GET /api/safety-limits` returns `limits`, `defaults` and `hardLimits`, and with a robot id the limits of that robot's model and `jogArmedUntil`. The sections are returned as the server sent them (maps, objects), because the server owns their shape; the clients do not copy the numbers into constants. `PUT /api/admin/safety-limits` takes a partial change (the server validates it and answers `400` for an unknown key, a wrong type or a value beyond the hard ceilings) and returns the limits now in force.

## Examples

```python
from hydra_umc_sdk import ClaimConflictError, JogNotArmedError, ServerClient

client = ServerClient("http://hydra.local:3000", token, controller_id="tab-1")
client.claim(1, ttl_ms=60000)
try:
    client.command(1, "jog", {"axis": "x", "amount": 5})
except JogNotArmedError:
    client.jog_arm(1, True)
except ClaimConflictError as refused:
    print(refused.code, refused.reservation.owner_username)
```

```typescript
import { HydraServerClient, JogNotArmedError } from "@hydra-umc/sdk";

const client = new HydraServerClient("http://hydra.local:3000", { token, controllerId: "tab-1" });
await client.claim(1, { ttlMs: 60000 });
try {
  await client.command(1, "jog", { params: { axis: "x", amount: 5 } });
} catch (error) {
  if (error instanceof JogNotArmedError) await client.jogArm(1, true);
}
```

## Blocks 2 to 5 of the second contract

The same four clients cover the rest of the second contract of the server (see its `docs/CONTRACT_V2.md`):

- **The revision of a robot.** `GET /api/robot/{id}` (`get_robot_request` / `getRobotRequest` / `GetRobotRequest` / `get_robot_request`, `robot()` on the client) answers the robot, its `revision` (also the `ETag`) and its cell.
- **Conditional writes.** `if_match` / `ifMatch` / `IfMatch` on `claim`, `release` and `command` sends `If-Match` (the revision quoted for you, or `*`). A robot that changed in between is a `412`: `RevisionMismatchError` (Rust: `ApiError::RevisionMismatch`) carries the current revision; read the robot again and retry. A `stop` is never conditional. The answers of `claim`, `release` and `command` carry the new `revision`.
- **The table command.** `table_command_request(robot, x, y, rz=None, mode="absolute"|"relative")` (client method `move_table` / `moveTable` / `MoveTable`) moves the XY table in one request and answers the position it ended in (`applied`). The server checks the move as a whole; a refusal is a `TableMoveError` (`table-invalid`, `table-out-of-limit`, `table-missing`) and nothing changed.
- **Safe mode of a robot.** `command_request(robot, "disable")` stops the robot and refuses its other commands (`423`, `robot-disabled`); `command_request(robot, "enable")` brings it back. `enable` is off by default on the server (`403`, `enable-not-allowed`) and then only an administrator may use it (`403`, `admin-required`); `disable` is open to every signed-in account, like a stop.
- **The audit record.** `audit_request(limit, after_seq, type, robot_id, verify)` and `audit()` read `GET /api/audit` (administrators) into entries with the account, controller id, address, robot and detail, plus the optional verification of the hash chain.
- **The `claims` message of the WebSocket.** For a client that opened `/ws` with `?remoteApiVersion=2`, `parse_claims_event` / `parseClaimsEvent` / `ParseClaimsEvent` reads the message into the same entries as `GET /api/claims` (now with `jogArmedUntil`) and answers nothing for any other message.

```python
view = client.robot(1)
try:
    client.move_table(1, 50, 60, if_match=view.revision)
except RevisionMismatchError as stale:
    view = client.robot(1)   # stale.revision is the current one
```

## Contract and tests

- `contracts/openapi/v1/server.openapi.json` (the typed slice, document version 1.3.0) describes the nine routes, the `X-Controller-Id` parameter, the `Reservation`, claim, arming and safety-limit schemas and the stable error codes. `contracts/openapi/v1/server.full.openapi.json` is a copy of the openapi that the server generates from its routes; the typed slice never invents a route the full copy does not have.
- `conformance/server-routes/cases.json` holds the request, invalid-request, error and response cases. `conformance/server-routes/cases_v2.json` does the same for blocks 2 to 5 (revision, `If-Match`, the table command, the audit record and the `claims` message). The Python, TypeScript, Go and Rust tests replay the same files, so the four clients build the same requests and tell the same errors apart. The Python tests also check every route against both OpenAPI documents, the body fields against the typed slice, the controller-id pattern against the client and that the stable codes are documented.
- The server's generated copy lists only `ttlMs`, `force` and `reason` for `claim` and does not list `controllerId` there; the typed slice does, because the server reads it.
