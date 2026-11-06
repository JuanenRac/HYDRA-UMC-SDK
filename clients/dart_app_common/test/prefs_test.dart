// =============================================================================
// HYDRA-UMC app common (Dart) - test/prefs_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The preferences both apps keep, over an in-memory store.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

import 'session_store_test.dart' show FakeSecure;

void main() {
  group('ClientPrefsCore', () {
    test('defaults, then what was saved', () async {
      final prefs = ClientPrefsCore(MemoryPrefsStore());
      expect(await prefs.loadConfirmPlay(), isTrue);
      expect(await prefs.loadHomeReset(false), isFalse);
      expect(await prefs.loadHomeReset(true), isTrue);
      expect(await prefs.loadConditionalMode(), isNull);
      expect(await prefs.loadControllerId(), isNull);
      await prefs.saveConfirmPlay(false);
      await prefs.saveHomeReset(true);
      await prefs.saveConditionalMode('prefer');
      await prefs.saveControllerId('ios-abc');
      expect(await prefs.loadConfirmPlay(), isFalse);
      expect(await prefs.loadHomeReset(false), isTrue);
      expect(await prefs.loadConditionalMode(), 'prefer');
      expect(await prefs.loadControllerId(), 'ios-abc');
    });

    test('the keys are the ones the apps have always written', () {
      expect(ClientPrefsCore.keyControllerId, 'hydra_controller_id');
      expect(ClientPrefsCore.keyConditionalMode, 'hydra_conditional_mode');
      expect(ClientPrefsCore.keyConfirmPlay, 'hydra_confirm_play');
      expect(ClientPrefsCore.keyHomeReset, 'hydra_home_reset_enabled');
    });
  });

  group('AuthPrefsCore', () {
    AuthPrefsCore make(MemoryPrefsStore store) =>
        AuthPrefsCore(store: store, session: SessionStore(secure: FakeSecure(), plain: store));

    test('the last server needs a host and a port', () async {
      final store = MemoryPrefsStore();
      final prefs = make(store);
      expect(await prefs.loadConnection(), isNull);
      await prefs.saveConnection('hydra.local', 18000);
      expect(await prefs.loadConnection(), ('hydra.local', 18000));
      store.values.remove('hydra_port');
      expect(await prefs.loadConnection(), isNull);
    });

    test('tls and biometric switches default to off', () async {
      final prefs = make(MemoryPrefsStore());
      expect(await prefs.loadUseTls(), isFalse);
      expect(await prefs.loadBiometricEnabled(), isFalse);
      await prefs.saveUseTls(true);
      await prefs.saveBiometricEnabled(true);
      expect(await prefs.loadUseTls(), isTrue);
      expect(await prefs.loadBiometricEnabled(), isTrue);
    });

    test('the session goes through the session store', () async {
      final prefs = make(MemoryPrefsStore());
      await prefs.saveToken('tok', 'ana', refreshToken: 'rt', replaceRefreshToken: true);
      expect(await prefs.loadToken(), 'tok');
      expect(await prefs.loadUsername(), 'ana');
      expect(await prefs.loadRefreshToken(), 'rt');
      await prefs.clearToken();
      expect(await prefs.loadToken(), isNull);
    });
  });
}
