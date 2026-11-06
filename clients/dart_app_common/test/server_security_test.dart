// =============================================================================
// HYDRA-UMC app common (Dart) - test/server_security_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The reading of the access options of the server, the body of a change and the changes that ask first.
// =============================================================================

import 'package:test/test.dart';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';

void main() {
  const full = '{"port":18000,"aiAccess":{"value":"open","source":"default"},'
      '"health":{"open":{"value":false,"source":"default"}},'
      '"safety":{"publishGlobalStop":{"value":false,"source":"config"}},'
      '"connections":{"recordAddress":{"value":false,"source":"default"}},'
      '"camera":{"open":{"value":false,"source":"default"},"credentialsViaEnv":{"value":true,"source":"default"}},'
      '"websocket":{"allowQueryToken":{"value":false,"source":"default"}},'
      '"logging":{"redactSecrets":{"value":true,"source":"default"}},'
      '"voice":{"includeHeardText":{"value":false,"source":"default"},"requireSignature":{"value":false,"source":"env"}},'
      '"install":{"newInstallTls":{"value":true,"source":"default"}}}';

  ServerSecurityOptions options() => ServerSecurity.parse(full)!;

  test('all nine options are read with where they come from', () {
    final o = options();
    expect(o.healthOpen!.value, isFalse);
    expect(o.healthOpen!.source, OptionSource.defaultValue);
    expect(o.publishGlobalStop!.source, OptionSource.config);
    expect(o.logRedaction!.value, isTrue);
    expect(o.voiceSignature!.locked, isTrue);
    expect(o.cameraOpen!.locked, isFalse);
    expect(o.isEmpty, isFalse);
  });

  test('a server that predates the options answers without them', () {
    final o = ServerSecurity.parse('{"port":18000,"aiAccess":{"value":"open","source":"default"}}')!;
    expect(o.isEmpty, isTrue);
    final v = o.toValues();
    expect(v.healthOpen, isFalse);
    expect(v.logRedaction, isTrue);
    expect(ServerSecurity.patch(o, v.copyWith(healthOpen: true)), isNull);
  });

  test('an option with a wrong type or an unknown source is left out and the rest still reads', () {
    final o = ServerSecurity.parse('{"health":{"open":{"value":"yes","source":"default"}},'
        '"camera":{"open":{"value":true,"source":"cloud"}},"logging":{"redactSecrets":{"value":false,"source":"config"}}}')!;
    expect(o.healthOpen, isNull);
    expect(o.cameraOpen, isNull);
    expect(o.logRedaction!.value, isFalse);
    expect(o.logRedaction!.source, OptionSource.config);
  });

  test('text that is not an object is not read', () {
    expect(ServerSecurity.parse('not json'), isNull);
    expect(ServerSecurity.parse(''), isNull);
    expect(ServerSecurity.parse('[]'), isNull);
  });

  test('the body holds only what changed', () {
    final o = options();
    expect(ServerSecurity.patch(o, o.toValues()), isNull);
    final body = ServerSecurity.patch(o, o.toValues().copyWith(healthOpen: true, recordAddress: true))!;
    expect(body.keys.toSet(), {'health', 'connections'});
    expect((body['health'] as Map)['open'], isTrue);
    expect((body['connections'] as Map)['recordAddress'], isTrue);
  });

  test('each option goes under the group the server reads it from', () {
    final body = ServerSecurity.patch(
      options(),
      const ServerSecurityValues(
        healthOpen: true,
        publishGlobalStop: true,
        recordAddress: true,
        cameraOpen: true,
        wsQueryToken: true,
        logRedaction: false,
        voiceSignature: true,
      ),
    )!;
    expect((body['safety'] as Map)['publishGlobalStop'], isTrue);
    expect((body['camera'] as Map)['open'], isTrue);
    expect((body['websocket'] as Map)['allowQueryToken'], isTrue);
    expect((body['logging'] as Map)['redactSecrets'], isFalse);
    // the signature is fixed by the environment of the server: it is never sent
    expect(body.containsKey('voice'), isFalse);
  });

  test('a value fixed by the environment is neither sent nor asked about', () {
    final o = options();
    expect(ServerSecurity.patch(o, o.toValues().copyWith(voiceSignature: false)), isNull);
    final fixedOn = ServerSecurity.parse('{"voice":{"requireSignature":{"value":true,"source":"env"}}}')!;
    expect(ServerSecurity.lowerings(fixedOn, fixedOn.toValues().copyWith(voiceSignature: false)), isEmpty);
    expect(ServerSecurity.patch(fixedOn, fixedOn.toValues().copyWith(voiceSignature: false)), isNull);
  });

  test('loosening a switch asks and tightening it or announcing a stop does not', () {
    final o = options();
    final v = o.toValues();
    expect(ServerSecurity.lowerings(o, v.copyWith(healthOpen: true)), [ProtectionLowering.healthOpen]);
    expect(ServerSecurity.lowerings(o, v.copyWith(recordAddress: true)), [ProtectionLowering.recordAddress]);
    expect(ServerSecurity.lowerings(o, v.copyWith(cameraOpen: true)), [ProtectionLowering.cameraOpen]);
    expect(ServerSecurity.lowerings(o, v.copyWith(wsQueryToken: true)), [ProtectionLowering.wsQueryToken]);
    expect(ServerSecurity.lowerings(o, v.copyWith(logRedaction: false)), [ProtectionLowering.logRedactionOff]);
    expect(ServerSecurity.lowerings(o, v.copyWith(publishGlobalStop: true)), isEmpty);

    final open = ServerSecurity.parse('{"health":{"open":{"value":true,"source":"config"}},'
        '"camera":{"open":{"value":true,"source":"config"}}}')!;
    expect(ServerSecurity.lowerings(open, open.toValues().copyWith(healthOpen: false, cameraOpen: false)), isEmpty);
    expect(ServerSecurity.patch(open, open.toValues().copyWith(healthOpen: false)), isNotNull);
  });

  test('several loosenings are listed in a fixed order', () {
    final o = options();
    final all = o.toValues().copyWith(healthOpen: true, recordAddress: true, cameraOpen: true, wsQueryToken: true, logRedaction: false);
    expect(ServerSecurity.lowerings(o, all), [
      ProtectionLowering.healthOpen,
      ProtectionLowering.recordAddress,
      ProtectionLowering.cameraOpen,
      ProtectionLowering.wsQueryToken,
      ProtectionLowering.logRedactionOff,
    ]);
  });

  test('the camera password and the TLS of a new installation are read and kept apart from the camera pictures', () {
    final o = options();
    expect(o.cameraCredentialsViaEnv!.value, isTrue);
    expect(o.newInstallTls!.value, isTrue);
    expect(o.cameraOpen!.value, isFalse);
    final old = ServerSecurity.parse('{"camera":{"open":{"value":true,"source":"config"}}}')!;
    expect(old.cameraCredentialsViaEnv, isNull);
    expect(old.newInstallTls, isNull);
    expect(old.toValues().cameraCredentialsViaEnv, isTrue);
    expect(old.toValues().newInstallTls, isTrue);
    expect(ServerSecurity.patch(old, old.toValues().copyWith(cameraCredentialsViaEnv: false, newInstallTls: false)), isNull);
  });

  test('the two options go under the groups the server reads them from, and only when they changed', () {
    final o = options();
    expect(ServerSecurity.patch(o, o.toValues()), isNull);
    final body = ServerSecurity.patch(o, o.toValues().copyWith(cameraCredentialsViaEnv: false, newInstallTls: false))!;
    expect((body['camera'] as Map)['credentialsViaEnv'], isFalse);
    expect((body['camera'] as Map).containsKey('open'), isFalse);
    expect((body['install'] as Map)['newInstallTls'], isFalse);
    expect(body.keys.toSet(), {'camera', 'install'});
  });

  test('taking either away asks, putting it back or a value fixed by the environment does not', () {
    final o = options();
    expect(ServerSecurity.lowerings(o, o.toValues().copyWith(cameraCredentialsViaEnv: false)),
        [ProtectionLowering.cameraCredentialsInArguments]);
    expect(ServerSecurity.lowerings(o, o.toValues().copyWith(newInstallTls: false)), [ProtectionLowering.newInstallTlsOff]);
    final loose = ServerSecurity.parse('{"camera":{"credentialsViaEnv":{"value":false,"source":"config"}},'
        '"install":{"newInstallTls":{"value":false,"source":"config"}}}')!;
    expect(ServerSecurity.lowerings(loose, loose.toValues().copyWith(cameraCredentialsViaEnv: true, newInstallTls: true)), isEmpty);
    final fixed = ServerSecurity.parse('{"camera":{"credentialsViaEnv":{"value":false,"source":"env"}},'
        '"install":{"newInstallTls":{"value":false,"source":"env"}}}')!;
    expect(fixed.cameraCredentialsViaEnv!.locked, isTrue);
    expect(ServerSecurity.lowerings(fixed, fixed.toValues().copyWith(cameraCredentialsViaEnv: true)), isEmpty);
    expect(ServerSecurity.patch(fixed, fixed.toValues().copyWith(cameraCredentialsViaEnv: true, newInstallTls: true)), isNull);
  });

  test('options are equal by value and source, and the instance methods agree with the static ones', () {
    expect(const ServerOption(true, OptionSource.config), const ServerOption(true, OptionSource.config));
    expect(const ServerOption(true, OptionSource.config) == const ServerOption(true, OptionSource.env), isFalse);
    final o = options();
    final next = o.toValues().copyWith(healthOpen: true);
    expect(o.patch(next), ServerSecurity.patch(o, next));
    expect(o.lowerings(next), ServerSecurity.lowerings(o, next));
    expect(ServerSecurityOptions.parse(full)!.toValues().healthOpen, o.toValues().healthOpen);
    expect(ServerSecurityOptions.parse('not json'), isNull);
  });
}
