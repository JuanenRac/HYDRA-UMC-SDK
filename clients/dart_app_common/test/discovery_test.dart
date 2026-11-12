// =============================================================================
// HYDRA-UMC app common (Dart) - test/discovery_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The subnet sweep and its prefixes with a fake probe and a fake list of interfaces: which networks are asked, which interfaces are left
// out, that every host is asked once, that a match is yielded and that a probe that throws does not stop the sweep.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

void main() {
  group('interfaces and prefixes', () {
    test('the mobile-data and VPN interface names are told apart', () {
      for (final name in ['pdp_ip0', 'rmnet_data1', 'ccmni0', 'wwan0', 'utun3', 'ipsec0', 'ppp0', 'tun0', 'tap1', 'wg0', 'WG0']) {
        expect(isMobileOrVpnInterface(name), isTrue, reason: name);
      }
      for (final name in ['en0', 'eth0', 'wlan0', 'Wi-Fi', 'bridge100']) {
        expect(isMobileOrVpnInterface(name), isFalse, reason: name);
      }
    });

    test('a prefix is the /24 of every IPv4 address, once, and the skipped interfaces leave theirs out', () {
      final interfaces = {
        'en0': ['192.168.0.12', '192.168.0.99'],
        'pdp_ip0': ['10.20.30.40'],
        'utun2': ['100.64.1.5'],
        'odd': ['not-an-address', '1.2.3'],
      };
      expect(prefixesOfInterfaces(interfaces), {'192.168.0', '10.20.30', '100.64.1'});
      expect(prefixesOfInterfaces(interfaces, skipMobileAndVpn: true), {'192.168.0'});
    });

    test('the candidates are the interfaces, then the last host, then the default when nothing is left', () async {
      expect(await candidatePrefixes(interfaces: () async => {'en0': ['192.168.0.12']}, lastHost: '10.0.0.7'), ['192.168.0', '10.0.0']);
      expect(await candidatePrefixes(interfaces: () async => {}), ['192.168.1']);
      expect(await candidatePrefixes(interfaces: () async => throw StateError('no interfaces')), ['192.168.1']);
      expect(await candidatePrefixes(interfaces: () async => {}, lastHost: 'not-an-address'), ['192.168.1']);
    });
  });

  group('the sweep', () {
    test('asks every host of every prefix once and yields what the probe recognises', () async {
      final asked = <String>[];
      final found = await scanSubnets(
        interfaces: () async => {'en0': ['192.168.5.20']},
        lastHost: '172.16.0.9',
        probe: (host, port) async {
          asked.add('$host:$port');
          return host == '192.168.5.77' ? ServerInfo(host: host, port: port, hostname: 'cell') : null;
        },
      ).toList();
      expect(found.map((s) => s.host), ['192.168.5.77']);
      expect(asked.length, 2 * 254);
      expect(asked.toSet().length, asked.length, reason: 'no host is asked twice');
      expect(asked, containsAll(['192.168.5.1:3000', '192.168.5.254:3000', '172.16.0.1:3000', '172.16.0.254:3000']));
    });

    test('a probe that throws does not stop the sweep and a custom port is used', () async {
      var calls = 0;
      final found = await scanSubnets(
        interfaces: () async => {'en0': ['10.1.1.5']},
        port: 3100,
        concurrency: 4,
        probe: (host, port) async {
          calls++;
          if (host == '10.1.1.3') throw StateError('answers with something unexpected');
          return host == '10.1.1.4' ? ServerInfo(host: host, port: port) : null;
        },
      ).toList();
      expect(calls, 254);
      expect(found.single.host, '10.1.1.4');
      expect(found.single.port, 3100);
    });

    test('leaves the mobile-data interfaces out when asked', () async {
      final prefixesAsked = <String>{};
      await scanSubnets(
        interfaces: () async => {'en0': ['192.168.7.2'], 'pdp_ip0': ['10.9.9.2']},
        skipMobileAndVpn: true,
        probe: (host, port) async {
          prefixesAsked.add(host.substring(0, host.lastIndexOf('.')));
          return null;
        },
      ).toList();
      expect(prefixesAsked, {'192.168.7'});
    });
  });
}
