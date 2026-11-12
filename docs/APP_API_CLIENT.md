# Shared API client of the Flutter apps

`clients/dart_app_common` holds the HTTP client of the HYDRA-UMC server that the Flutter apps share. It is pure Dart: it imports no `package:http` and no Flutter plugin. Everything platform-specific enters through small interfaces that each app injects.

| Piece | What it does |
|---|---|
| `HttpTransport` (`HttpRequestData` / `HttpResponseData`) | Sends one request and answers. The app wraps `package:http` (or any test double) behind it. Timeouts are applied by the client. |
| `RenewingTransport` | Decorates a transport: a request that carried a bearer token and was answered with an expired or invalid session (401, or 403 `TOKEN_EXPIRED` / `TOKEN_INVALID`) asks the `TokenRenewer` for a new token and is sent once more. Any other answer and a failed renewal reach the caller untouched. |
| `CommandSequence` | Numbers the motion commands (`seq`): always above the previous number and not below the clock. |
| `HydraApiCore` | Headers (client tag, bearer, controller id, `If-Match`), the numbering, the renewal, the reading of error answers (`HydraApiException`) and the endpoints every app calls (login, refresh, logout, settings, robot command, claim, release, jog arming, stop-all, metrics, text and JSON helpers). |
| `HydraError` / `HydraErrorKind` | The typed error an app's view model reports (kind and raw parameters, no text). Each app maps it to its own localized sentence. |
| `ConnectionHistory` | The clients and sign-in events the server lists; times are milliseconds (UTC) with `DateTime` views. |
| `ServerSecurity` (`ServerSecurityOptions`, `ServerSecurityValues`) | Reading, patching and the "asks first" rules of the nine access switches of the server. |
| `PrefsStore`, `ClientPrefsCore`, `AuthPrefsCore` | The ordinary preferences (last server, TLS and biometric switches, controller id, confirm-PLAY, HOME/RESET, conditional mode) over an injected store; the session stays in `SessionStore`. |
| `SecureTokenBackend` / `SessionPlainStore` (`SessionStore`) | The stored session; see `SESSION_STORE.md`. |

An app extends `HydraApiCore`: it adds its typed endpoints, overrides `resolveScheme()` (the choice between http and https stays in the app, with its TLS policy) and keeps its own public API. The conformance vectors in `conformance/api-client/vectors.json` (command numbering, which answers mean an expired session, how error answers are read, the renewal conversation) are replayed by the Dart package tests; a native app that talks to the same server (the Kotlin Android app) can replay them against its own client.

What stays in each app on purpose: the adapters over `package:http`, `flutter_secure_storage` (with its platform options) and `shared_preferences`; the TLS policy and certificate pinning (`tls_settings`, which needs `dart:io`); the localized texts of `HydraError`; the view model; and the robot command contract of the app while the two apps differ in the functions they offer.

## Decisions behind the shared types

- **Transport, not plugin.** The API client never imports `package:http`. An app wraps its client (with its TLS pinning) in an `HttpTransport`; tests use a scripted one. The same seam is used for preferences (`PrefsStore`) and secrets (`SecureTokenBackend`).
- **Numbering and renewal are common behaviour.** Every app numbers the motion commands and renews an expired session once; an app that has no owner for the session leaves `tokenRenewer` null and nothing changes.
- **Times are milliseconds.** `ConnectionClient` and `ConnectionEvent` keep UTC milliseconds (cheap to compare, no time zone); `firstSeen`, `lastSeen` and `at` give the `DateTime`, and `ConnectionHistory.agoDates` is the date form of `ago`.
- **Server options keep both call styles.** `ServerSecurity.parse/patch/lowerings` (static) and `ServerSecurityOptions.parse/patch/lowerings` (static and instance) do the same thing; the source of a default value is `OptionSource.defaultValue`.
- **The error type has no text.** `HydraErrorKind` holds the kinds of both apps; an app gives the kinds it never builds a neutral text.
- **Not shared yet:** the robot command contract of the Flutter apps (the DSI one is a subset of the iOS one until the panel offers the same functions), the view models, and the discovery of servers.
- **Discovery needs `dart:io` and `multicast_dns`.** `discovery` finds servers by mDNS and by a sweep of the /24 networks of the device. The app supplies the probe (`ServerProbe`: its own read of the identity of the server, with its TLS policy), the package supplies the prefixes, the interface rules (mobile-data and VPN interfaces can be left out), the concurrency and the never-throw behaviour. A platform that drops multicast receive (iOS without its entitlement) leaves the mDNS path empty and the sweep is the path that always works.
- **TLS settings need `dart:io`.** `tls_settings` (the settings, the fingerprint and PEM rules, the pinned `HttpClient`, the reading of a server certificate) is the one module that imports `dart:io` and `package:http`, so it is not available to a web build. The choices are stored through `TlsPrefsCore` over a `PrefsStore`, with the same keys the apps already write, so an app swaps its own copy for the package without losing a saved setting. The apps move to it with the next tag of the SDK.
