# Shared API client of the Flutter apps

`clients/dart_app_common` holds the HTTP client of the HYDRA-UMC server that the Flutter apps share. It is pure Dart: it imports no `package:http` and no Flutter plugin. Everything platform-specific enters through small interfaces that each app injects.

| Piece | What it does |
|---|---|
| `HttpTransport` (`HttpRequestData` / `HttpResponseData`) | Sends one request and answers. The app wraps `package:http` (or any test double) behind it. Timeouts are applied by the client. |
| `RenewingTransport` | Decorates a transport: a request that carried a bearer token and was answered with an expired or invalid session (401, or 403 `TOKEN_EXPIRED` / `TOKEN_INVALID`) asks the `TokenRenewer` for a new token and is sent once more. Any other answer and a failed renewal reach the caller untouched. |
| `CommandSequence` | Numbers the motion commands (`seq`): always above the previous number and not below the clock. |
| `HydraApiCore` | Headers (client tag, bearer, controller id, `If-Match`), the numbering, the renewal, the reading of error answers (`HydraApiException`) and the endpoints every app calls (login, refresh, logout, settings, robot command, claim, release, jog arming, stop-all, metrics, text and JSON helpers). |
| `SecureTokenBackend` / `SessionPlainStore` (`SessionStore`) | The stored session; see `SESSION_STORE.md`. |

An app extends `HydraApiCore`: it adds its typed endpoints, overrides `resolveScheme()` (the choice between http and https stays in the app, with its TLS policy) and keeps its own public API. The conformance vectors in `conformance/api-client/vectors.json` (command numbering, which answers mean an expired session, how error answers are read, the renewal conversation) are replayed by the Dart package tests; a native app that talks to the same server (the Kotlin Android app) can replay them against its own client.
