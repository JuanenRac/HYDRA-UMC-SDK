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
