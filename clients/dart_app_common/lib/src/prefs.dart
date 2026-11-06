// =============================================================================
// HYDRA-UMC app common (Dart) - src/prefs.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// What the Flutter apps keep in their ordinary preferences, with the storage
// injected: the last server (host, port, TLS), the biometric switch, the
// controller id and the switches both apps have. The platform's preference
// store (shared_preferences) is wrapped by each app in a [PrefsStore]; secrets
// stay in the [SecureTokenBackend] of the stored session. An app extends
// [ClientPrefsCore] with the switches only it has.
// =============================================================================

import 'session_store.dart';

/// Ordinary key/value preferences (the seam the apps fill with shared_preferences
/// and the tests with a map).
abstract class PrefsStore implements SessionPlainStore {
  Future<int?> getInt(String key);
  Future<void> setInt(String key, int value);
  Future<void> setString(String key, String value);
}

/// A [PrefsStore] over a map (tests and previews).
class MemoryPrefsStore implements PrefsStore {
  MemoryPrefsStore([Map<String, Object>? initial]) : values = {...?initial};

  final Map<String, Object> values;

  @override
  Future<bool?> getBool(String key) async => values[key] as bool?;
  @override
  Future<int?> getInt(String key) async => values[key] as int?;
  @override
  Future<String?> getString(String key) async => values[key] as String?;
  @override
  Future<void> setBool(String key, bool value) async => values[key] = value;
  @override
  Future<void> setInt(String key, int value) async => values[key] = value;
  @override
  Future<void> setString(String key, String value) async => values[key] = value;
  @override
  Future<void> remove(String key) async => values.remove(key);
}

/// The switches and ids both apps keep.
class ClientPrefsCore {
  ClientPrefsCore(this.store);

  /// The storage behind these preferences (an app's extra switches use it too).
  final PrefsStore store;

  static const keyControllerId = 'hydra_controller_id';
  static const keyConditionalMode = 'hydra_conditional_mode';
  static const keyConfirmPlay = 'hydra_confirm_play';
  static const keyHomeReset = 'hydra_home_reset_enabled';

  Future<bool> loadBool(String key, bool defaultValue) async => (await store.getBool(key)) ?? defaultValue;
  Future<void> saveBool(String key, bool value) => store.setBool(key, value);

  /// Ask before PLAY (on unless switched off).
  Future<bool> loadConfirmPlay() => loadBool(keyConfirmPlay, true);
  Future<void> saveConfirmPlay(bool value) => saveBool(keyConfirmPlay, value);

  /// The HOME/RESET gesture (the default comes from the contract).
  Future<bool> loadHomeReset(bool defaultValue) => loadBool(keyHomeReset, defaultValue);
  Future<void> saveHomeReset(bool value) => saveBool(keyHomeReset, value);

  /// How conditional writes (If-Match) are used; null when never chosen.
  Future<String?> loadConditionalMode() => store.getString(keyConditionalMode);
  Future<void> saveConditionalMode(String mode) => store.setString(keyConditionalMode, mode);

  /// The id of this installation, kept so a reservation made here can be
  /// released after a restart.
  Future<String?> loadControllerId() => store.getString(keyControllerId);
  Future<void> saveControllerId(String id) => store.setString(keyControllerId, id);
}

/// The last server and the session of an app: connection and biometric
/// preferences over a [PrefsStore], the session over a [SessionStore].
class AuthPrefsCore {
  AuthPrefsCore({required this.store, required this._session});

  final PrefsStore store;
  final SessionStore _session;

  static const keyHost = 'hydra_host';
  static const keyPort = 'hydra_port';
  static const keyUseTls = 'hydra_use_tls';
  static const keyBiometricEnabled = 'hydra_biometric_enabled';

  Future<void> saveConnection(String host, int port) async {
    await store.setString(keyHost, host);
    await store.setInt(keyPort, port);
  }

  Future<(String, int)?> loadConnection() async {
    final host = await store.getString(keyHost);
    final port = await store.getInt(keyPort);
    if (host == null || port == null) return null;
    return (host, port);
  }

  Future<void> saveUseTls(bool useTls) => store.setBool(keyUseTls, useTls);
  Future<bool> loadUseTls() async => (await store.getBool(keyUseTls)) ?? false;

  Future<void> saveBiometricEnabled(bool enabled) => store.setBool(keyBiometricEnabled, enabled);
  Future<bool> loadBiometricEnabled() async => (await store.getBool(keyBiometricEnabled)) ?? false;

  Future<void> saveToken(String token, String username, {String? refreshToken, bool replaceRefreshToken = false}) =>
      _session.saveSession(token, username, refreshToken: refreshToken, replaceRefreshToken: replaceRefreshToken);

  Future<void> purgeStaleKeychainOnFirstRun() => _session.purgeStaleSessionOnFirstRun();
  Future<String?> loadToken() => _session.loadToken();
  Future<String?> loadUsername() => _session.loadUsername();
  Future<String?> loadRefreshToken() => _session.loadRefreshToken();
  Future<void> clearToken() => _session.clearSession();
}
