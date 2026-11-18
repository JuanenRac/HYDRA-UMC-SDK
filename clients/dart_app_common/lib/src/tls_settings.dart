// =============================================================================
// HYDRA-UMC app common (Dart) - src/tls_settings.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// How the Flutter apps reach the server, and what they trust.
//
//   - HTTPS (and WSS) first, always. Plain HTTP/WS is used only when the user
//     turned it on (allowPlainHttp, off by default), and only toward a server
//     on the local network unless allowPlainRemote is on too: the session
//     token would otherwise travel readable across the Internet.
//   - A server with a self-signed certificate is trusted by its SHA-256
//     fingerprint (pinnedFingerprint). The fingerprint is read from the
//     server once, shown to the person, and kept only after they confirm it
//     (trust on first use). From then on only a certificate with exactly that
//     fingerprint is accepted; host name and issuer are not checked, the
//     fingerprint is the identity.
//   - Fingerprints are kept per server (pinnedFingerprints, "host:port" ->
//     fingerprint), so two self-signed servers can both be trusted. The single
//     pinnedFingerprint of older versions still applies to every server that
//     has no entry of its own, and is moved to the last server by
//     TlsPrefsCore.load when the app tells which server that was.
//   - A server with a fingerprint is not offered plain HTTP/WS (a downgrade
//     would make the pin meaningless) unless allowPlainWithPin is on, which is
//     off by default.
//   - Without a fingerprint, customCaPem (a PEM with one or more CA
//     certificates) replaces the system certificates as the only trusted
//     issuer. With neither, the system certificates decide.
//
// The settings are kept through a [PrefsStore] ([TlsPrefsCore]); each app
// fills that seam with its own preference storage.
// =============================================================================

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http/io_client.dart';

import 'prefs.dart';
import 'sha256.dart';

/// The TLS choices of the person using the app.
class TlsSettings {
  /// Allows plain HTTP/WS after HTTPS has been tried. Off: only HTTPS is used.
  final bool allowPlainHttp;

  /// Allows plain HTTP/WS to a server outside the local network (needs
  /// [allowPlainHttp]). Off by default.
  final bool allowPlainRemote;

  /// SHA-256 of the one server certificate to accept, as 64 lowercase hex
  /// digits; empty for none.
  final String pinnedFingerprint;

  /// PEM text with the certificates of the only issuers to trust; empty for
  /// the system certificates.
  final String customCaPem;

  /// The fingerprint to accept for each server, by [serverKey] (`host:port`),
  /// as 64 lowercase hex digits. A server with an entry here uses it instead
  /// of [pinnedFingerprint].
  final Map<String, String> pinnedFingerprints;

  /// Allows plain HTTP/WS to a server that has a pinned fingerprint (outside
  /// this machine). Off by default: a pinned server is reached over TLS only.
  final bool allowPlainWithPin;

  const TlsSettings({
    this.allowPlainHttp = false,
    this.allowPlainRemote = false,
    this.pinnedFingerprint = '',
    this.customCaPem = '',
    this.pinnedFingerprints = const <String, String>{},
    this.allowPlainWithPin = false,
  });

  /// The key of a server in [pinnedFingerprints]: lowercase `host:port`.
  static String serverKey(String host, int port) => '${host.trim().toLowerCase()}:$port';

  /// The fingerprint to accept for [host]:[port]: the one of that server, else
  /// the single fingerprint of older versions; empty for none.
  String pinFor(String host, int port) {
    final own = pinnedFingerprints[serverKey(host, port)];
    if (own != null && own.trim().isNotEmpty) return own;
    return pinnedFingerprint;
  }

  /// True when [host] (any server when null) has a fingerprint.
  bool hasPinFor([String? host]) {
    if (pinnedFingerprint.trim().isNotEmpty) return true;
    if (host == null) return pinnedFingerprints.values.any((v) => v.trim().isNotEmpty);
    final prefix = '${host.trim().toLowerCase()}:';
    return pinnedFingerprints.entries.any((e) => e.key.startsWith(prefix) && e.value.trim().isNotEmpty);
  }

  /// What is wrong with these settings, or null when they can be saved. Blank
  /// fields are fine.
  TlsProblem? validate() {
    if (pinnedFingerprint.trim().isNotEmpty && TlsFingerprint.normalize(pinnedFingerprint) == null) {
      return TlsProblem.fingerprintInvalid;
    }
    for (final entry in pinnedFingerprints.entries) {
      if (entry.value.trim().isNotEmpty && TlsFingerprint.normalize(entry.value) == null) {
        return TlsProblem.fingerprintInvalid;
      }
    }
    if (customCaPem.trim().isNotEmpty && TlsPem.parse(customCaPem).isEmpty) {
      return TlsProblem.caInvalid;
    }
    return null;
  }

  /// The settings with the fingerprint in its canonical form and the PEM trimmed.
  TlsSettings normalized() => TlsSettings(
        allowPlainHttp: allowPlainHttp,
        allowPlainRemote: allowPlainHttp && allowPlainRemote,
        pinnedFingerprint: TlsFingerprint.normalize(pinnedFingerprint) ?? pinnedFingerprint.trim(),
        customCaPem: customCaPem.trim(),
        pinnedFingerprints: {
          for (final e in pinnedFingerprints.entries)
            if (e.value.trim().isNotEmpty) e.key.trim().toLowerCase(): TlsFingerprint.normalize(e.value) ?? e.value.trim(),
        },
        allowPlainWithPin: allowPlainWithPin,
      );

  TlsSettings copyWith({
    bool? allowPlainHttp,
    bool? allowPlainRemote,
    String? pinnedFingerprint,
    String? customCaPem,
    Map<String, String>? pinnedFingerprints,
    bool? allowPlainWithPin,
  }) =>
      TlsSettings(
        allowPlainHttp: allowPlainHttp ?? this.allowPlainHttp,
        allowPlainRemote: allowPlainRemote ?? this.allowPlainRemote,
        pinnedFingerprint: pinnedFingerprint ?? this.pinnedFingerprint,
        customCaPem: customCaPem ?? this.customCaPem,
        pinnedFingerprints: pinnedFingerprints ?? this.pinnedFingerprints,
        allowPlainWithPin: allowPlainWithPin ?? this.allowPlainWithPin,
      );

  /// The settings with the fingerprint of [host]:[port] set (an empty
  /// [fingerprint] removes it).
  TlsSettings withPin(String host, int port, String fingerprint) {
    final map = {...pinnedFingerprints};
    final key = serverKey(host, port);
    if (fingerprint.trim().isEmpty) {
      map.remove(key);
    } else {
      map[key] = fingerprint;
    }
    return copyWith(pinnedFingerprints: map);
  }

  /// Whether a plain (unencrypted) connection to [host] is allowed. Traffic to
  /// this same machine (loopback) never leaves it and is always allowed; the
  /// rest needs [allowPlainHttp], and a host outside the local network needs
  /// [allowPlainRemote] too. A host with a pinned fingerprint (see
  /// [hasPinFor]) is reached over TLS only, unless [allowPlainWithPin] is on.
  bool plainAllowedFor(String host) {
    if (TlsPolicy.isLoopback(host)) return true;
    if (hasPinFor(host) && !allowPlainWithPin) return false;
    return allowPlainHttp && (allowPlainRemote || TlsPolicy.isLocalHost(host));
  }

  @override
  bool operator ==(Object other) =>
      other is TlsSettings &&
      other.allowPlainHttp == allowPlainHttp &&
      other.allowPlainRemote == allowPlainRemote &&
      other.pinnedFingerprint == pinnedFingerprint &&
      other.customCaPem == customCaPem &&
      other.allowPlainWithPin == allowPlainWithPin &&
      _sameMap(other.pinnedFingerprints, pinnedFingerprints);

  @override
  int get hashCode => Object.hash(
        allowPlainHttp,
        allowPlainRemote,
        pinnedFingerprint,
        customCaPem,
        allowPlainWithPin,
        Object.hashAllUnordered(pinnedFingerprints.entries.map((e) => Object.hash(e.key, e.value))),
      );

  static bool _sameMap(Map<String, String> a, Map<String, String> b) {
    if (a.length != b.length) return false;
    for (final e in a.entries) {
      if (b[e.key] != e.value) return false;
    }
    return true;
  }
}

enum TlsProblem { fingerprintInvalid, caInvalid }

/// The settings the clients read when they are created; the view model fills
/// it when the app starts and when the person saves a change.
class TlsSettingsStore {
  static TlsSettings current = const TlsSettings();
}

/// SHA-256 fingerprints of certificates.
class TlsFingerprint {
  static final _hex64 = RegExp(r'^[0-9a-f]{64}$');

  /// Lowercase hex without separators, or null when [input] is not 64
  /// hexadecimal digits (colons, spaces and dashes are ignored).
  static String? normalize(String input) {
    final cleaned = input.replaceAll(RegExp(r'[:\-\s]'), '').toLowerCase();
    return _hex64.hasMatch(cleaned) ? cleaned : null;
  }

  /// The fingerprint of a DER encoded certificate.
  static String ofDer(List<int> der) => sha256Hex(der);

  /// The usual display form: uppercase pairs separated by colons.
  static String display(String hex) {
    final upper = hex.toUpperCase();
    final pairs = <String>[];
    for (var i = 0; i + 1 < upper.length; i += 2) {
      pairs.add(upper.substring(i, i + 2));
    }
    return pairs.join(':');
  }

  /// Equal strings, compared without stopping at the first difference.
  static bool equal(String a, String b) {
    if (a.length != b.length) return false;
    var diff = 0;
    for (var i = 0; i < a.length; i++) {
      diff |= a.codeUnitAt(i) ^ b.codeUnitAt(i);
    }
    return diff == 0;
  }
}

/// PEM certificates.
class TlsPem {
  static final _block = RegExp(r'-----BEGIN CERTIFICATE-----([\s\S]*?)-----END CERTIFICATE-----');

  /// The DER bytes of every certificate in [pem]; empty when the text holds
  /// none or is damaged.
  static List<Uint8List> parse(String pem) {
    final result = <Uint8List>[];
    for (final match in _block.allMatches(pem)) {
      final body = match.group(1)!.replaceAll(RegExp(r'\s'), '');
      if (body.isEmpty) return const [];
      try {
        final der = base64.decode(body);
        if (der.isEmpty) return const [];
        result.add(der);
      } on FormatException {
        return const [];
      }
    }
    return result;
  }
}

/// Where a server is: decides when plain traffic may be used at all.
class TlsPolicy {
  /// True for the address of this same machine.
  static bool isLoopback(String host) {
    var h = host.trim().toLowerCase();
    if (h.startsWith('[') && h.endsWith(']')) h = h.substring(1, h.length - 1);
    return h == 'localhost' || h == '::1' || RegExp(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$').hasMatch(h);
  }

  /// True for loopback, private (RFC 1918), link-local and unique-local
  /// addresses, and for single-label or .local/.lan/.home.arpa names.
  static bool isLocalHost(String host) {
    var h = host.trim().toLowerCase();
    if (h.startsWith('[') && h.endsWith(']')) h = h.substring(1, h.length - 1);
    if (h.isEmpty) return false;
    if (h == 'localhost') return true;
    if (h.contains(':')) return h == '::1' || h.startsWith('fe80:') || h.startsWith('fc') || h.startsWith('fd');
    final octets = h.split('.');
    if (octets.length == 4 && octets.every((o) => int.tryParse(o) != null && int.parse(o) >= 0 && int.parse(o) <= 255)) {
      final a = int.parse(octets[0]);
      final b = int.parse(octets[1]);
      return a == 10 || a == 127 || (a == 172 && b >= 16 && b <= 31) || (a == 192 && b == 168) || (a == 169 && b == 254);
    }
    // an incomplete or odd number, not a name
    if (octets.every((o) => o.isNotEmpty && RegExp(r'^\d+$').hasMatch(o))) return false;
    return octets.length == 1 || h.endsWith('.local') || h.endsWith('.lan') || h.endsWith('.home.arpa');
  }
}

/// Loads and saves [TlsSettings] through a [PrefsStore]. Nothing stored means
/// the defaults: HTTPS only, no fingerprint, no CA.
class TlsPrefsCore {
  TlsPrefsCore(this.store);

  final PrefsStore store;

  static const keyAllowPlain = 'hydra_tls_allow_plain_http';
  static const keyAllowPlainRemote = 'hydra_tls_allow_plain_remote';
  static const keyPin = 'hydra_tls_pinned_fingerprint';
  static const keyCa = 'hydra_tls_custom_ca_pem';

  /// The fingerprints by server, as a JSON object `{"host:port": "<hex>"}`.
  static const keyPins = 'hydra_tls_pinned_fingerprints';
  static const keyAllowPlainWithPin = 'hydra_tls_allow_plain_with_pin';

  /// Reads the settings. The single fingerprint of older versions stays stored
  /// under [keyPin] (going back to an older app loses nothing); when the app
  /// says which server was the last one ([lastServerHost], [lastServerPort])
  /// and that server has no fingerprint of its own, the single fingerprint
  /// becomes the fingerprint of that server and stops applying to the others.
  Future<TlsSettings> load({String? lastServerHost, int? lastServerPort}) async {
    var legacy = await store.getString(keyPin) ?? '';
    final pins = _decodePins(await store.getString(keyPins));
    if (legacy.trim().isNotEmpty && lastServerHost != null && lastServerPort != null) {
      final key = TlsSettings.serverKey(lastServerHost, lastServerPort);
      if (!pins.containsKey(key)) {
        pins[key] = legacy;
        legacy = '';
        await store.setString(keyPins, _encodePins(pins));
      }
    }
    return TlsSettings(
      allowPlainHttp: await store.getBool(keyAllowPlain) ?? false,
      allowPlainRemote: await store.getBool(keyAllowPlainRemote) ?? false,
      pinnedFingerprint: legacy,
      customCaPem: await store.getString(keyCa) ?? '',
      pinnedFingerprints: pins,
      allowPlainWithPin: await store.getBool(keyAllowPlainWithPin) ?? false,
    );
  }

  Future<void> save(TlsSettings settings) async {
    await store.setBool(keyAllowPlain, settings.allowPlainHttp);
    await store.setBool(keyAllowPlainRemote, settings.allowPlainRemote);
    await store.setString(keyPin, settings.pinnedFingerprint);
    await store.setString(keyCa, settings.customCaPem);
    await store.setString(keyPins, _encodePins(settings.pinnedFingerprints));
    await store.setBool(keyAllowPlainWithPin, settings.allowPlainWithPin);
  }

  static Map<String, String> _decodePins(String? text) {
    if (text == null || text.trim().isEmpty) return <String, String>{};
    try {
      final decoded = jsonDecode(text);
      if (decoded is! Map) return <String, String>{};
      return {
        for (final e in decoded.entries)
          if (e.key is String && e.value is String) e.key as String: e.value as String,
      };
    } on FormatException {
      return <String, String>{};
    }
  }

  static String _encodePins(Map<String, String> pins) => jsonEncode(pins);
}

/// A dart:io HttpClient that follows [settings]: the pinned fingerprint if
/// there is one, else the custom CA if there is one, else the system
/// certificates. Unusable settings are never applied (the system rules stay).
///
/// With [host] and [port] the fingerprint is the one of that server (its own
/// entry, else the single one of older versions) and only that certificate is
/// trusted. Without them, the single fingerprint applies to every server as
/// before; when only per-server fingerprints exist, the system (or custom CA)
/// rules decide and a certificate they refuse is accepted only if it is the one
/// pinned for the very server the client is connecting to.
HttpClient createHttpClient([TlsSettings? settings, String? host, int? port]) {
  final s = settings ?? TlsSettingsStore.current;
  final pin = TlsFingerprint.normalize(host != null && port != null ? s.pinFor(host, port) : s.pinnedFingerprint);
  if (pin != null) {
    final context = SecurityContext(withTrustedRoots: false);
    final client = HttpClient(context: context);
    client.badCertificateCallback = (X509Certificate cert, String host, int port) =>
        pinMatches(pin, cert.der, cert.startValidity, cert.endValidity);
    return client;
  }
  final authorities = TlsPem.parse(s.customCaPem);
  HttpClient client;
  if (authorities.isNotEmpty) {
    final context = SecurityContext(withTrustedRoots: false);
    try {
      context.setTrustedCertificatesBytes(utf8.encode(s.customCaPem.trim()));
      client = HttpClient(context: context);
    } on TlsException {
      client = HttpClient();
    }
  } else {
    client = HttpClient();
  }
  _trustPerServerPins(client, s);
  return client;
}

/// Lets a certificate the normal rules refuse through when it is the one pinned
/// for the server being connected to (the callback is told which one).
void _trustPerServerPins(HttpClient client, TlsSettings s) {
  if (s.pinnedFingerprints.isEmpty) return;
  client.badCertificateCallback = (X509Certificate cert, String host, int port) {
    final pin = TlsFingerprint.normalize(s.pinnedFingerprints[TlsSettings.serverKey(host, port)] ?? '');
    return pin != null && pinMatches(pin, cert.der, cert.startValidity, cert.endValidity);
  };
}

/// True when [der] has the fingerprint [pinHex] and [now] is inside the
/// validity of the certificate.
bool pinMatches(String pinHex, List<int> der, DateTime notBefore, DateTime notAfter, [DateTime? now]) {
  if (!TlsFingerprint.equal(TlsFingerprint.ofDer(der), pinHex)) return false;
  final at = now ?? DateTime.now();
  return !at.isBefore(notBefore) && !at.isAfter(notAfter);
}

/// An http.Client that follows [settings] (or [TlsSettingsStore.current]); give
/// [host] and [port] to use the fingerprint of that server.
http.Client createClient([TlsSettings? settings, String? host, int? port]) => IOClient(createHttpClient(settings, host, port));

/// An http.Client for looking for servers: it accepts any certificate, because
/// it only reads the public identity of a host and sends no credential. What
/// is trusted for the real connection is decided later, by the settings.
http.Client createDiscoveryClient() {
  final client = HttpClient();
  client.badCertificateCallback = (X509Certificate cert, String host, int port) => true;
  return IOClient(client);
}

/// What was learned by looking at the certificate a server presents.
class ServerCertificate {
  final String fingerprint;
  final String subject;
  final DateTime notBefore;
  final DateTime notAfter;
  const ServerCertificate(this.fingerprint, this.subject, this.notBefore, this.notAfter);
}

/// Connects to [host]:[port] over TLS and returns the certificate the server
/// presents, without trusting it and without sending anything: the person
/// compares its fingerprint with the one the server shows and then decides.
/// Null when no TLS connection could be made.
Future<ServerCertificate?> fetchServerCertificate(
  String host,
  int port, {
  Duration timeout = const Duration(seconds: 5),
}) async {
  try {
    final socket = await SecureSocket.connect(
      host,
      port,
      timeout: timeout,
      onBadCertificate: (_) => true,
    );
    try {
      final cert = socket.peerCertificate;
      if (cert == null) return null;
      return ServerCertificate(
        TlsFingerprint.ofDer(cert.der),
        cert.subject,
        cert.startValidity,
        cert.endValidity,
      );
    } finally {
      socket.destroy();
    }
  } catch (_) {
    return null;
  }
}

/// True when [error] says the server's certificate was refused (as opposed to
/// a server that does not speak TLS at all).
bool isCertificateRejection(Object error) {
  final text = '$error'.toUpperCase();
  return text.contains('CERTIFICATE_VERIFY_FAILED') || text.contains('BAD CERTIFICATE') || text.contains('CERTIFICATE');
}

/// True when [error] looks like a failure to set up or trust TLS, as opposed
/// to a server that is simply not there.
bool isTlsFailure(Object error) {
  if (error is HandshakeException || error is TlsException) return true;
  final text = '$error'.toUpperCase();
  return text.contains('CERTIFICATE_VERIFY_FAILED') ||
      text.contains('HANDSHAKEEXCEPTION') ||
      text.contains('WRONG_VERSION_NUMBER') ||
      text.contains('TLSV1_ALERT');
}
