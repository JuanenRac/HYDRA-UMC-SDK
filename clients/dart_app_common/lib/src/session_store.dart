// =============================================================================
// HYDRA-UMC app common (Dart) - src/session_store.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The rules of the stored session shared by the mobile apps: what is kept, in
// which order it is written and erased, and what a read returns when the
// platform's secure storage fails. The platform keeps its own secure storage
// (Keychain, Secret Service, DPAPI) behind [SecureTokenBackend]; the schema is
// documented in docs/SESSION_STORE.md and checked by the vectors in
// conformance/session-store/vectors.json, which the Android app replays too.
//
// Rules, in short:
//  * Token, user name and refresh token live only in secure storage. A failed
//    secure write never falls back to a plain file: the session then lives in
//    memory for the current run only.
//  * A plain marker ("logged out") is the source of truth for an ended
//    session. It is set BEFORE the secure delete is attempted, so a delete that
//    fails can never bring the old session back.
//  * Saving without a refresh token keeps the stored one; a real sign-in
//    (replaceRefreshToken) removes it, so a refresh token left by a previous
//    account can not become valid for the next one.
//  * A save that fails half way reverts what it wrote.
// =============================================================================

/// Secure key/value storage of the platform (the seam the tests replace).
abstract class SecureTokenBackend {
  Future<void> write(String key, String value);
  Future<String?> read(String key);
  Future<void> delete(String key);
}

/// Ordinary (not secret) key/value storage: markers and the legacy copy of a
/// session saved before secure storage was used.
abstract class SessionPlainStore {
  Future<bool?> getBool(String key);
  Future<String?> getString(String key);
  Future<void> setBool(String key, bool value);
  Future<void> remove(String key);
}

/// The logical keys of the schema. The physical keys of a platform that
/// stores them differently are listed in docs/SESSION_STORE.md.
class SessionKeys {
  const SessionKeys._();
  static const token = 'hydra_token';
  static const username = 'hydra_username';
  static const refreshToken = 'hydra_refresh_token';
  static const loggedOut = 'hydra_logged_out';
  static const installMarker = 'hydra_install_marker';
}

class SessionStore {
  SessionStore({
    required this._secure,
    required this._plain,
    void Function(String message)? log,
  }) : _log = log ?? ((_) {});

  final SecureTokenBackend _secure;
  final SessionPlainStore _plain;
  final void Function(String message) _log;

  // Kept only for this object's lifetime (one app run); never written to disk.
  String? _memToken;
  String? _memUsername;
  String? _memRefresh;

  /// Stores the session. [refreshToken] null keeps the stored one;
  /// [replaceRefreshToken] true makes a null [refreshToken] erase it (a real
  /// sign-in).
  Future<void> saveSession(
    String token,
    String username, {
    String? refreshToken,
    bool replaceRefreshToken = false,
  }) async {
    var tokenWritten = false;
    var usernameWritten = false;
    try {
      await _secure.write(SessionKeys.token, token);
      tokenWritten = true;
      await _secure.write(SessionKeys.username, username);
      usernameWritten = true;
      if (refreshToken != null) {
        await _secure.write(SessionKeys.refreshToken, refreshToken);
      } else if (replaceRefreshToken) {
        await _secure.delete(SessionKeys.refreshToken);
      }
      // Secure storage is the source of truth now: drop a stale plain copy
      // and any in-memory session of an earlier failure.
      await _plain.remove(SessionKeys.token);
      await _plain.remove(SessionKeys.username);
      await _plain.remove(SessionKeys.loggedOut);
      _memToken = null;
      _memUsername = null;
      if (refreshToken != null || replaceRefreshToken) _memRefresh = null;
    } catch (e) {
      if (tokenWritten) {
        try {
          await _secure.delete(SessionKeys.token);
        } catch (_) {}
      }
      if (usernameWritten) {
        try {
          await _secure.delete(SessionKeys.username);
        } catch (_) {}
      }
      _log(
        'SessionStore: secure storage write failed ($e) - the session is NOT '
        'persisted (never a plain fallback); it lasts until the app restarts.',
      );
      _memToken = token;
      _memUsername = username;
      if (refreshToken != null || replaceRefreshToken) _memRefresh = refreshToken;
    }
  }

  Future<String?> loadToken() async {
    if (_memToken != null) return _memToken;
    if (await _plain.getBool(SessionKeys.loggedOut) ?? false) return null;
    String? secureToken;
    try {
      secureToken = await _secure.read(SessionKeys.token);
    } catch (e) {
      _log('SessionStore: secure storage read failed ($e) - in-memory session only.');
    }
    if (secureToken != null) return secureToken;

    // A session saved before secure storage was used may sit in the plain
    // store: move it in and remove the old copy (reading old data, not a new
    // plain write).
    final legacyToken = await _plain.getString(SessionKeys.token);
    if (legacyToken == null) return null;
    final legacyUsername = await _plain.getString(SessionKeys.username);
    try {
      await _secure.write(SessionKeys.token, legacyToken);
      if (legacyUsername != null) {
        await _secure.write(SessionKeys.username, legacyUsername);
      }
      await _plain.remove(SessionKeys.token);
      await _plain.remove(SessionKeys.username);
    } catch (e) {
      _log('SessionStore: could not move the legacy token to secure storage ($e).');
    }
    return legacyToken;
  }

  Future<String?> loadUsername() async {
    if (_memUsername != null) return _memUsername;
    if (await _plain.getBool(SessionKeys.loggedOut) ?? false) return null;
    try {
      final secureUsername = await _secure.read(SessionKeys.username);
      if (secureUsername != null) return secureUsername;
    } catch (e) {
      _log('SessionStore: secure storage read failed ($e) - in-memory session only.');
    }
    return _plain.getString(SessionKeys.username);
  }

  /// The refresh token, or null: a session without one is a normal state.
  /// Secure storage only, no plain fallback.
  Future<String?> loadRefreshToken() async {
    if (_memRefresh != null) return _memRefresh;
    if (await _plain.getBool(SessionKeys.loggedOut) ?? false) return null;
    try {
      return await _secure.read(SessionKeys.refreshToken);
    } catch (e) {
      _log('SessionStore: secure storage read failed ($e) - no refresh token.');
      return null;
    }
  }

  /// Ends the session. The marker is set first, so the end is honoured even
  /// when the secure delete fails.
  Future<void> clearSession() async {
    _memToken = null;
    _memUsername = null;
    _memRefresh = null;
    await _plain.setBool(SessionKeys.loggedOut, true);
    try {
      await _secure.delete(SessionKeys.token);
      await _secure.delete(SessionKeys.username);
      await _secure.delete(SessionKeys.refreshToken);
    } catch (e) {
      _log('SessionStore: secure delete failed ($e) - the session is ended by the marker anyway.');
    }
    await _plain.remove(SessionKeys.token);
    await _plain.remove(SessionKeys.username);
  }

  /// For platforms whose secure storage outlives an uninstall (iOS Keychain):
  /// on the first launch of a fresh installation the session left by the
  /// previous one is erased instead of resumed.
  Future<void> purgeStaleSessionOnFirstRun() async {
    if (await _plain.getBool(SessionKeys.installMarker) ?? false) return;
    try {
      await _secure.delete(SessionKeys.token);
      await _secure.delete(SessionKeys.username);
      await _secure.delete(SessionKeys.refreshToken);
    } catch (e) {
      _log('SessionStore: could not clear the previous installation\'s session ($e).');
    }
    await _plain.setBool(SessionKeys.installMarker, true);
  }
}
