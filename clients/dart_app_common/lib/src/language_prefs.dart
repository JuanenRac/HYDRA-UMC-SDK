// =============================================================================
// HYDRA-UMC app common (Dart) - src/language_prefs.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The language the person chose in an app, kept across launches. The store is injected and the languages the app
// ships are given by the app: this package knows no Flutter localizations.
// =============================================================================

import 'prefs.dart';

class LanguagePrefsCore {
  LanguagePrefsCore(this.store);

  /// The storage behind the choice.
  final PrefsStore store;

  static const keyLanguage = 'hydra_language';

  /// Keeps [languageCode]; null removes the choice, so the app follows the language of the system again.
  Future<void> saveLanguage(String? languageCode) => languageCode == null ? store.remove(keyLanguage) : store.setString(keyLanguage, languageCode);

  /// The chosen language when it is one of [supported]; null when there is no choice or the app no longer ships it.
  Future<String?> loadLanguageCode(Iterable<String> supported) async {
    final code = await store.getString(keyLanguage);
    return code != null && supported.contains(code) ? code : null;
  }
}
