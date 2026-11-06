// =============================================================================
// HYDRA-UMC app common (Dart) - src/pairing_link.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// What the admin page of the server puts in its QR code: where the server is, the fingerprint of its TLS certificate (so
// the first connection is pinned instead of trusted blindly) and a name to show.
//
//     hydra-umc://pair?host=192.168.0.180&port=3000&fp=<64 hex digits>&name=Workshop
//
// The fingerprint is required (unlike the Android app, which still accepts a link without one).
//
// This file only reads and checks the text; it connects to nothing and keeps nothing. The limits default to the ones in
// the shared command contract; an app checks in a test that its own generated constants say the same.
// =============================================================================

/// The limits of what a pairing link may hold.
class PairingLimits {
  const PairingLimits({
    this.scheme = 'hydra-umc',
    this.host = 'pair',
    this.maxPayloadChars = 600,
    this.nameMax = 64,
    this.portMin = 1,
    this.portMax = 65535,
  });

  final String scheme;
  final String host;
  final int maxPayloadChars;
  final int nameMax;
  final int portMin;
  final int portMax;

  static const PairingLimits standard = PairingLimits();
}

/// What a link offers. [fingerprint] is the canonical (lowercase, no separators) SHA-256 of the certificate; a link
/// without one is never accepted (the first connection is always pinned, never trusted blindly).
class PairingOffer {
  final String host;
  final int port;
  final String fingerprint;
  final String name;
  const PairingOffer(this.host, this.port, this.fingerprint, this.name);

  bool get usesPinning => true;
}

enum PairingProblem {
  empty,
  tooLong,
  notAPairingLink,
  missingHost,
  badHost,
  badPort,
  badFingerprint,
  missingFingerprint,
  badName,
  repeatedField,
  badEncoding,
}

/// The result of reading a link: an offer or the reason it was refused.
class PairingResult {
  final PairingOffer? offer;
  final PairingProblem? problem;
  const PairingResult.ok(PairingOffer this.offer) : problem = null;
  const PairingResult.refused(PairingProblem this.problem) : offer = null;

  bool get isOk => offer != null;
}

/// Lowercase hex without separators, or null when [input] is not 64 hexadecimal digits (colons, spaces and dashes are ignored).
String? normalizeFingerprint(String input) {
  final cleaned = input.replaceAll(RegExp(r'[:\-\s]'), '').toLowerCase();
  return RegExp(r'^[0-9a-f]{64}$').hasMatch(cleaned) ? cleaned : null;
}

class PairingLink {
  PairingLink._();

  static final RegExp _hostName = RegExp(r'^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$');
  static final RegExp _ipv4 = RegExp(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$');
  static final RegExp _ipv6 = RegExp(r'^[0-9A-Fa-f:]{2,45}$');
  static const Set<String> _known = {'host', 'port', 'fp', 'name'};

  static String _prefix(PairingLimits limits) => '${limits.scheme}://${limits.host}';

  /// True when [text] looks like a pairing link (it may still be refused by [parse]).
  static bool looksLikePairing(String? text, {PairingLimits limits = PairingLimits.standard}) =>
      text != null && text.trim().toLowerCase().startsWith('${_prefix(limits)}?');

  static PairingResult parse(String? input, {PairingLimits limits = PairingLimits.standard}) {
    final text = (input ?? '').trim();
    if (text.isEmpty) return const PairingResult.refused(PairingProblem.empty);
    if (text.length > limits.maxPayloadChars) return const PairingResult.refused(PairingProblem.tooLong);
    if (!looksLikePairing(text, limits: limits)) return const PairingResult.refused(PairingProblem.notAPairingLink);
    var query = text.substring(_prefix(limits).length + 1);
    final hash = query.indexOf('#');
    if (hash >= 0) query = query.substring(0, hash);
    final fields = <String, String>{};
    for (final pair in query.split('&')) {
      if (pair.isEmpty) continue;
      final eq = pair.indexOf('=');
      final key = (eq < 0 ? pair : pair.substring(0, eq)).toLowerCase();
      final raw = eq < 0 ? '' : pair.substring(eq + 1);
      final String value;
      try {
        value = Uri.decodeQueryComponent(raw);
      } catch (_) {
        return const PairingResult.refused(PairingProblem.badEncoding);
      }
      // Only the four known fields count; a repeated one is refused so a link cannot say two things.
      if (_known.contains(key)) {
        if (fields.containsKey(key)) return const PairingResult.refused(PairingProblem.repeatedField);
        fields[key] = value;
      }
    }
    var host = (fields['host'] ?? '').trim();
    if (host.startsWith('[')) host = host.substring(1);
    if (host.endsWith(']')) host = host.substring(0, host.length - 1);
    if (host.isEmpty) return const PairingResult.refused(PairingProblem.missingHost);
    if (!_validHost(host)) return const PairingResult.refused(PairingProblem.badHost);
    final portText = (fields['port'] ?? '').trim();
    final port = RegExp(r'^\d{1,5}$').hasMatch(portText) ? int.tryParse(portText) : null;
    if (port == null || port < limits.portMin || port > limits.portMax) {
      return const PairingResult.refused(PairingProblem.badPort);
    }
    final fpText = (fields['fp'] ?? '').trim();
    // The fingerprint is mandatory: without it the link is refused, there is no "pair anyway" mode.
    if (fpText.isEmpty) return const PairingResult.refused(PairingProblem.missingFingerprint);
    final fingerprint = normalizeFingerprint(fpText);
    if (fingerprint == null) return const PairingResult.refused(PairingProblem.badFingerprint);
    final name = (fields['name'] ?? '').trim();
    if (name.runes.length > limits.nameMax || name.runes.any(_isControl)) {
      return const PairingResult.refused(PairingProblem.badName);
    }
    return PairingResult.ok(PairingOffer(host, port, fingerprint, name.isEmpty ? host : name));
  }

  static bool _isControl(int rune) => rune < 0x20 || (rune >= 0x7f && rune <= 0x9f);

  static bool _validHost(String host) {
    final v4 = _ipv4.firstMatch(host);
    if (v4 != null) return [for (var i = 1; i <= 4; i++) int.parse(v4.group(i)!)].every((n) => n >= 0 && n <= 255);
    if (host.contains(':')) return _ipv6.hasMatch(host);
    return _hostName.hasMatch(host);
  }
}
