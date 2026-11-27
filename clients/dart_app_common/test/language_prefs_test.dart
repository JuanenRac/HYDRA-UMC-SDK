// =============================================================================
// HYDRA-UMC app common (Dart) - test/language_prefs_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The saved language: kept, removed and ignored when the app does not ship it.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

void main() {
  const supported = ['en', 'es', 'pt'];

  test('with no choice there is no language', () async {
    expect(await LanguagePrefsCore(MemoryPrefsStore()).loadLanguageCode(supported), isNull);
  });

  test('a choice is kept under the key the apps already use', () async {
    final store = MemoryPrefsStore();
    await LanguagePrefsCore(store).saveLanguage('pt');
    expect(store.values['hydra_language'], 'pt');
    expect(await LanguagePrefsCore(store).loadLanguageCode(supported), 'pt');
  });

  test('saving no language removes the choice', () async {
    final store = MemoryPrefsStore({'hydra_language': 'es'});
    await LanguagePrefsCore(store).saveLanguage(null);
    expect(store.values.containsKey('hydra_language'), isFalse);
  });

  test('a language the app does not ship is ignored and not erased', () async {
    final store = MemoryPrefsStore({'hydra_language': 'xx'});
    expect(await LanguagePrefsCore(store).loadLanguageCode(supported), isNull);
    expect(store.values['hydra_language'], 'xx');
  });
}
