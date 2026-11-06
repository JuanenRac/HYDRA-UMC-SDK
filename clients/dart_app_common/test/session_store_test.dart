// =============================================================================
// HYDRA-UMC app common (Dart) - test/session_store_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// Replays conformance/session-store/vectors.json against SessionStore and
// adds the cases that only a Dart implementation has (plain legacy copy,
// install marker).
// =============================================================================

import 'dart:convert';
import 'dart:io';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

class FakeSecure implements SecureTokenBackend {
  final Map<String, String> data = {};
  bool unavailable = false;
  bool deleteFails = false;
  Set<String> writeFails = {};

  @override
  Future<void> write(String key, String value) async {
    if (unavailable || writeFails.contains(key)) throw Exception('secure storage unavailable');
    data[key] = value;
  }

  @override
  Future<String?> read(String key) async {
    if (unavailable) throw Exception('secure storage unavailable');
    return data[key];
  }

  @override
  Future<void> delete(String key) async {
    if (unavailable || deleteFails) throw Exception('secure storage unavailable');
    data.remove(key);
  }
}

class FakePlain implements SessionPlainStore {
  final Map<String, Object> data = {};
  @override
  Future<bool?> getBool(String key) async => data[key] as bool?;
  @override
  Future<String?> getString(String key) async => data[key] as String?;
  @override
  Future<void> setBool(String key, bool value) async => data[key] = value;
  @override
  Future<void> remove(String key) async => data.remove(key);
}

const _logical = {
  'token': SessionKeys.token,
  'username': SessionKeys.username,
  'refresh': SessionKeys.refreshToken,
};

void main() {
  final file = File('../../conformance/session-store/vectors.json');
  final doc = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;

  test('the vector file is the version this test knows', () {
    expect(doc['version'], 1);
  });

  for (final raw in doc['vectors'] as List) {
    final vector = raw as Map<String, dynamic>;
    // This implementation can fail its secure storage and clears the user name,
    // so it replays every vector whatever it requires.
    test(vector['name'] as String, () async {
      final secure = FakeSecure();
      final plain = FakePlain();
      var store = SessionStore(secure: secure, plain: plain);
      for (final raw in vector['steps'] as List) {
        final step = raw as Map<String, dynamic>;
        switch (step['op']) {
          case 'login':
            await store.saveSession(step['token'] as String, step['username'] as String,
                refreshToken: step['refresh'] as String?, replaceRefreshToken: true);
          case 'renew':
            await store.saveSession(step['token'] as String, step['username'] as String,
                refreshToken: step['refresh'] as String?);
          case 'logout':
            await store.clearSession();
          case 'restart':
            store = SessionStore(secure: secure, plain: plain);
          case 'faults':
            secure.unavailable = step['unavailable'] == true;
            secure.deleteFails = step['delete'] == true;
            secure.writeFails = {
              for (final k in (step['write_fails'] as List?)?.cast<String>() ?? const <String>[]) _logical[k]!,
            };
          case 'expect':
            if (step.containsKey('token')) expect(await store.loadToken(), step['token'], reason: 'token');
            if (step.containsKey('username')) expect(await store.loadUsername(), step['username'], reason: 'username');
            if (step.containsKey('refresh')) expect(await store.loadRefreshToken(), step['refresh'], reason: 'refresh');
          default:
            fail('unknown operation ${step['op']}');
        }
      }
    });
  }

  test('a session saved in the plain store is moved into secure storage on first read', () async {
    final secure = FakeSecure();
    final plain = FakePlain()
      ..data[SessionKeys.token] = 'old'
      ..data[SessionKeys.username] = 'ana';
    final store = SessionStore(secure: secure, plain: plain);
    expect(await store.loadToken(), 'old');
    expect(secure.data[SessionKeys.token], 'old');
    expect(secure.data[SessionKeys.username], 'ana');
    expect(plain.data.containsKey(SessionKeys.token), isFalse);
  });

  test('the legacy plain copy is kept when secure storage is unavailable', () async {
    final secure = FakeSecure()..unavailable = true;
    final plain = FakePlain()..data[SessionKeys.token] = 'old';
    final store = SessionStore(secure: secure, plain: plain);
    expect(await store.loadToken(), 'old');
    expect(plain.data[SessionKeys.token], 'old');
  });

  test('a plain write never happens when the secure write fails', () async {
    final secure = FakeSecure()..unavailable = true;
    final plain = FakePlain();
    await SessionStore(secure: secure, plain: plain).saveSession('t', 'u', refreshToken: 'r');
    expect(plain.data.keys.where((k) => k != SessionKeys.loggedOut), isEmpty);
  });

  test('the first run of a fresh installation erases a session left in secure storage once', () async {
    final secure = FakeSecure()
      ..data[SessionKeys.token] = 'left'
      ..data[SessionKeys.username] = 'ana'
      ..data[SessionKeys.refreshToken] = 'r';
    final plain = FakePlain();
    final store = SessionStore(secure: secure, plain: plain);
    await store.purgeStaleSessionOnFirstRun();
    expect(secure.data, isEmpty);
    secure.data[SessionKeys.token] = 'new';
    await store.purgeStaleSessionOnFirstRun();
    expect(secure.data[SessionKeys.token], 'new');
  });
}
