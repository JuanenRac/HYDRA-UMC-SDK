# The stored session of the mobile apps

The Android app, the iOS app and the touch panel keep the same few values after a sign-in, and they have to treat them the same way: a fix to the handling of the token has to land in all three. Each platform keeps its own secure storage; what is shared is the schema, the rules below and the vectors that check them.

## What is stored

| Logical field | Where | Secret | Dart key | Android key |
|---|---|---|---|---|
| access token | secure storage | yes | `hydra_token` | `token` |
| user name | secure storage | no, but tied to the session | `hydra_username` | `username` |
| refresh token | secure storage | yes | `hydra_refresh_token` | `refresh_token` |
| session ended | plain marker | no | `hydra_logged_out` | the token and the refresh token are written empty |
| installation seen | plain marker | no | `hydra_install_marker` | not needed |
| server host and port, scheme | plain | no | `hydra_host`, `hydra_port`, `hydra_use_tls` | the connection history |
| pinned server fingerprint | the TLS settings of the app | no | `hydra_tls_pinned_fingerprint` | `pinned_fingerprint` |

The pinned fingerprint is not part of the session: signing out does not forget which server the app trusts. The Android app also keeps the saved password and the e-mail of the "remember me" option in its encrypted store; the Dart apps do not keep a password.

## Rules

1. **Secure storage only.** The token, the user name and the refresh token are never written to a plain file. When the secure write fails the session lives in memory until the app closes, and the next start asks for a sign-in.
2. **A save that fails half way reverts what it wrote**, so the secure storage never holds half of a session.
3. **Saving without a refresh token keeps the stored one** (a renewal). A real sign-in erases it when the answer carries none, so a refresh token left by a previous account can not become valid for the next one.
4. **Signing out sets the marker first**, then deletes. A delete that fails can not bring the session back: every read looks at the marker before it looks at the storage. A new sign-in clears the marker.
5. **Reads never invent a session**: an absent value is "none", not an error; a failing read is logged and answers "none".
6. **A copy from before secure storage was used** (a plain token) is moved in on the first read and removed from the plain store.
7. **A fresh installation does not resume the session of the previous one** where the secure storage outlives an uninstall (the iOS Keychain): the first launch erases it once.

Platform differences are kept, not hidden. The Android app has no failing secure storage to model (the encrypted store resets itself when its key is lost) and keeps the user name after a sign-out to fill the form; the Dart apps forget it.

## Where it lives

- Dart: `SessionStore` in `clients/dart_app_common` (`SecureTokenBackend` and `SessionPlainStore` are the seams); the iOS app and the touch panel build their `AuthPrefs` on it.
- Kotlin: `SessionFields` in the Android app implements the same rules over the encrypted store.
- Vectors: `conformance/session-store/vectors.json`. Each vector is a sequence of `login`, `renew`, `logout`, `restart`, `faults` and `expect` steps. A vector may list `requires` for abilities a platform lacks (`secure_faults`, `username_after_logout_cleared`); the platform skips those and says so. Both implementations replay the file in their tests, so a rule changes in the vectors first.
