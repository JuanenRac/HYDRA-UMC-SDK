// =============================================================================
// HYDRA-UMC app common (Dart) - src/discovery.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// Finds servers on the local network, by two independent paths that feed the same "Scan local network" sheet of the apps:
//   - discoverMdns(): mDNS/Bonjour query for the "_hydra._tcp.local" service the server publishes. Near-instant when the network
//     delivers multicast replies. A platform may drop multicast receive for an app without the entitlement it asks for (iOS, per
//     app): the query then goes out and no reply comes, and the function finishes with nothing found.
//   - scanSubnets(): one probe against every host of the /24 networks of the device. Slower, but needs no multicast, so it is
//     the path that always works. The prefixes come from the network interfaces of the device (dart:io, no permission and no
//     plugin) and fall back to 192.168.1.x only when the enumeration returns nothing, as on a locked-down simulator.
// Both paths verify what they find with the probe the app hands in (its own GET of the identity of the server), so a match is
// never assumed live because a name answered. Neither throws on a failure: they yield what they found.
// =============================================================================

import 'dart:async';
import 'dart:io';

import 'package:multicast_dns/multicast_dns.dart';

import 'server_info.dart';

/// The probe an app supplies: reads the identity of the server at [host]:[port] and gives it as a [ServerInfo], or null when
/// nothing that is a server answers there. It must not throw for an unreachable host (a thrown error is taken as null).
typedef ServerProbe = Future<ServerInfo?> Function(String host, int port);

/// The service type the server publishes.
const String mdnsServiceType = '_hydra._tcp.local';

/// The port a subnet sweep asks.
const int defaultDiscoveryPort = 3000;

/// How many hosts a sweep asks at the same time.
const int scanConcurrency = 32;

/// True for the interface names the platforms give to the mobile-data link (`pdp_ip*`, `rmnet*`, `ccmni*`, `wwan*`) and to VPN or
/// tunnel interfaces (`utun*`, `ipsec*`, `ppp*`, `tun*`, `tap*`, `wg*`).
bool isMobileOrVpnInterface(String name) {
  final n = name.toLowerCase();
  const prefixes = ['pdp_ip', 'rmnet', 'ccmni', 'wwan', 'utun', 'ipsec', 'ppp', 'tun', 'tap', 'wg'];
  return prefixes.any(n.startsWith);
}

/// The /24 prefix ("a.b.c") of every IPv4 address in [interfaces] (name -> addresses), leaving out the mobile-data and VPN ones when
/// [skipMobileAndVpn] is true.
Set<String> prefixesOfInterfaces(Map<String, List<String>> interfaces, {bool skipMobileAndVpn = false}) {
  final prefixes = <String>{};
  for (final entry in interfaces.entries) {
    if (skipMobileAndVpn && isMobileOrVpnInterface(entry.key)) continue;
    for (final address in entry.value) {
      final parts = address.split('.');
      if (parts.length == 4) prefixes.add(parts.sublist(0, 3).join('.'));
    }
  }
  return prefixes;
}

/// Lists the non-loopback IPv4 interfaces of the device as name -> addresses.
typedef InterfaceLister = Future<Map<String, List<String>>> Function();

Future<Map<String, List<String>>> _systemInterfaces() async {
  final interfaces = await NetworkInterface.list(type: InternetAddressType.IPv4, includeLoopback: false);
  return {for (final iface in interfaces) iface.name: iface.addresses.map((a) => a.address).toList()};
}

/// Every distinct /24 prefix worth scanning: the interfaces of the device first, then the subnet of [lastHost] if it differs, then
/// the common default, so a fresh install with no saved host and an interface query that comes back empty still tries something
/// instead of scanning nothing.
Future<List<String>> candidatePrefixes({String? lastHost, bool skipMobileAndVpn = false, InterfaceLister? interfaces}) async {
  final prefixes = <String>{};
  try {
    prefixes.addAll(prefixesOfInterfaces(await (interfaces ?? _systemInterfaces)(), skipMobileAndVpn: skipMobileAndVpn));
  } catch (_) {
    // No usable interface information (sandboxed platform, no network): fall through to the fallbacks below.
  }
  if (lastHost != null) {
    final parts = lastHost.split('.');
    if (parts.length == 4) prefixes.add(parts.sublist(0, 3).join('.'));
  }
  if (prefixes.isEmpty) prefixes.add('192.168.1');
  return prefixes.toList();
}

Future<ServerInfo?> _probe(ServerProbe probe, String host, int port) async {
  try {
    return await probe(host, port);
  } catch (_) {
    return null;
  }
}

/// Queries mDNS/Bonjour for HYDRA-UMC servers and resolves every instance found to a [ServerInfo] with [probe], so a match is
/// verified exactly as [scanSubnets] verifies its own. Any failure along the way yields nothing instead of throwing.
Stream<ServerInfo> discoverMdns({required ServerProbe probe, Duration timeout = const Duration(seconds: 4)}) async* {
  final client = MDnsClient();
  final seen = <String>{};
  try {
    await client.start();
    final ptrQuery = client
        .lookup<PtrResourceRecord>(ResourceRecordQuery.serverPointer(mdnsServiceType))
        .timeout(timeout, onTimeout: (sink) => sink.close());
    await for (final ptr in ptrQuery) {
      final srvQuery = client
          .lookup<SrvResourceRecord>(ResourceRecordQuery.service(ptr.domainName))
          .timeout(timeout, onTimeout: (sink) => sink.close());
      await for (final srv in srvQuery) {
        final ipQuery = client
            .lookup<IPAddressResourceRecord>(ResourceRecordQuery.addressIPv4(srv.target))
            .timeout(timeout, onTimeout: (sink) => sink.close());
        await for (final ip in ipQuery) {
          final host = ip.address.address;
          final port = srv.port;
          if (!seen.add('$host:$port')) continue;
          final info = await _probe(probe, host, port);
          if (info != null) yield info;
        }
      }
    }
  } catch (_) {
    // Best-effort path: see the header.
  } finally {
    client.stop();
  }
}

/// Asks every host of every candidate /24 (see [candidatePrefixes]) with [probe], yielding each match as soon as it is found rather
/// than waiting for the whole sweep. With [skipMobileAndVpn] the mobile-data and VPN interfaces of the phone are left out of the
/// sweep (off by default, which scans every interface).
Stream<ServerInfo> scanSubnets({
  required ServerProbe probe,
  String? lastHost,
  bool skipMobileAndVpn = false,
  int port = defaultDiscoveryPort,
  int concurrency = scanConcurrency,
  InterfaceLister? interfaces,
}) async* {
  final prefixes = await candidatePrefixes(lastHost: lastHost, skipMobileAndVpn: skipMobileAndVpn, interfaces: interfaces);
  for (final prefix in prefixes) {
    final hosts = List.generate(254, (i) => '$prefix.${i + 1}');
    var index = 0;
    final controller = StreamController<ServerInfo>();
    Future<void> worker() async {
      while (index < hosts.length) {
        final host = hosts[index++];
        final info = await _probe(probe, host, port);
        if (info != null && !controller.isClosed) controller.add(info);
      }
    }

    final workers = List.generate(concurrency, (_) => worker());
    unawaited(Future.wait(workers).whenComplete(controller.close));
    yield* controller.stream;
  }
}
