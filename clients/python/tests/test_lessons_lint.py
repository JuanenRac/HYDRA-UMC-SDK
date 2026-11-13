"""Light tests of lessons_lint.py: toy repositories in temporary folders. Every rule has a positive case, a clean case and its documented false positive."""
import contextlib
import io
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

def _find_tool_folder() -> str:
    """The folder that holds the tool: beside the tests, in a sibling tools/ folder or in tools/canonical/ of a parent."""
    for up in Path(__file__).resolve().parents[:4]:
        for cand in (up, up / "tools", up / "tools" / "canonical"):
            if (cand / "lessons_lint.py").is_file():
                return str(cand)
    return str(Path(__file__).resolve().parent.parent)


sys.path.insert(0, _find_tool_folder())
import lessons_lint as ll  # noqa: E402


class Repo:
    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "toy"
        for rel, content in files.items():
            p = self.path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")

    def __enter__(self):
        return self.path

    def __exit__(self, *exc):
        self.tmp.cleanup()


def run(files, rules, **kw):
    with Repo(files) as repo:
        return ll.lint_repo(repo, rules, **kw)


class SubprocessTimeout(unittest.TestCase):
    def test_flags_missing_timeout_in_all_forms(self):
        src = ("import subprocess\nimport subprocess as sp\nfrom subprocess import run as r, check_output\n"
               "subprocess.run(['a'])\nsp.check_call(['b'])\nr(['c'])\ncheck_output(['d'])\nsubprocess.call(['e'])\n")
        res = run({"x.py": src}, ["subprocess-timeout"])
        self.assertEqual([f["line"] for f in res["findings"]], [4, 5, 6, 7, 8])

    def test_clean_with_timeout_or_unknown_kwargs_or_pragma(self):
        src = ("import subprocess\nsubprocess.run(['a'], timeout=5)\nsubprocess.run(['b'], **kw)\n"
               "subprocess.run(['c'])  # lessons: ok\nsubprocess.Popen(['d'])\n")
        self.assertEqual(run({"x.py": src}, ["subprocess-timeout"])["findings"], [])

    def test_ignores_other_objects_named_run(self):
        src = "import subprocess\nclass A:\n    def run(self): ...\nA().run()\nrunner.run(['x'])\n"
        self.assertEqual(run({"x.py": src}, ["subprocess-timeout"])["findings"], [])

    def test_known_false_positive_wrapper_with_timeout_in_kwargs_dict_is_skipped_but_long_installer_is_flagged(self):
        # documented: an installer that must run long is reported until it carries the pragma
        src = "import subprocess\nsubprocess.run(['installer.exe', '/S'])\n"
        self.assertEqual(len(run({"x.py": src}, ["subprocess-timeout"])["findings"]), 1)

    def test_skips_hidden_dirs_and_bad_syntax(self):
        files = {"node_modules/a.py": "import subprocess\nsubprocess.run(['a'])\n", "bad.py": "def (:\n"}
        self.assertEqual(run(files, ["subprocess-timeout"])["findings"], [])


CATALOG = {f"locales/{l}.json": {"k.a": "a", "k.b": "b"} for l in ll.LANGS}


class VisibleText(unittest.TestCase):
    SRC = "import i18n\nprint('Connection refused by the server')\nprint(i18n.t('k.a'))\nprint('OK')\nprint('KEY=value')\nimport sys\nsys.exit('Something went wrong here')\nsys.exit(2)\n"

    def test_flags_sentences_only_in_repos_with_catalog(self):
        res = run({"app.py": self.SRC, **CATALOG}, ["visible-text"])
        self.assertEqual([f["line"] for f in res["findings"]], [2, 7])
        self.assertEqual(run({"app.py": self.SRC}, ["visible-text"])["findings"], [])   # without a catalogue the rule does not apply

    def test_only_files_that_import_i18n_and_not_tests(self):
        files = {"cli.py": self.SRC.replace("import i18n\n", ""), "tests/test_a.py": self.SRC, "test_b.py": self.SRC, **CATALOG}
        self.assertEqual(run(files, ["visible-text"])["findings"], [])

    def test_argparse_help_and_pragma(self):
        src = "import i18n, argparse\np = argparse.ArgumentParser(description='Shows the state of things')\nprint('Hello there world')  # lessons: ok\n"
        res = run({"a.py": src, **CATALOG}, ["visible-text"])
        self.assertEqual([f["line"] for f in res["findings"]], [2])

    def test_known_false_positive_proper_name_with_two_words(self):
        res = run({"a.py": "import i18n\nprint('Electro Hobby')\n", **CATALOG}, ["visible-text"])
        self.assertEqual(len(res["findings"]), 1)   # known false positive: solved with the pragma


class CoverageFloor(unittest.TestCase):
    PYPROJECT = "[tool.coverage.report]\nfail_under = 90\n"

    def test_floor_above_measured_is_flagged(self):
        res = run({"pyproject.toml": self.PYPROJECT}, ["coverage-floor"], measured=88.0)
        self.assertEqual(len(res["findings"]), 1)
        self.assertIn("90", res["findings"][0]["message"])

    def test_floor_at_or_below_measured_is_clean(self):
        self.assertEqual(run({"pyproject.toml": self.PYPROJECT}, ["coverage-floor"], measured=90.0)["findings"], [])
        self.assertEqual(run({"pyproject.toml": self.PYPROJECT}, ["coverage-floor"], measured=95.2)["findings"], [])

    def test_floor_from_workflow_and_measured_from_files(self):
        wf = "jobs:\n  a:\n    steps:\n      - run: python -m coverage report --fail-under=85\n"
        res = run({".github/workflows/ci.yml": wf, ".lessons_coverage.json": {"measured": 78}}, ["coverage-floor"])
        self.assertEqual(len(res["findings"]), 1)
        res = run({".github/workflows/ci.yml": wf, "coverage.json": {"totals": {"percent_covered": 86.1}}}, ["coverage-floor"])
        self.assertEqual(res["findings"], [])
        res = run({".github/workflows/ci.yml": wf, "coverage.xml": '<coverage line-rate="0.80" branch-rate="0">'}, ["coverage-floor"])
        self.assertEqual(len(res["findings"]), 1)

    def test_highest_floor_wins(self):
        wf = "      - run: coverage report --fail-under=70\n"
        res = run({"pyproject.toml": self.PYPROJECT, ".github/workflows/a.yml": wf}, ["coverage-floor"], measured=80)
        self.assertEqual(len(res["findings"]), 1)

    def test_no_measurement_only_informs(self):
        res = run({"pyproject.toml": self.PYPROJECT}, ["coverage-floor"])
        self.assertEqual(res["findings"], [])
        self.assertTrue(res["notes"])

    def test_known_false_positive_stale_measurement(self):
        # documented: an old measure (another branch) with a floor legitimately raised is reported
        self.assertEqual(len(run({"pyproject.toml": "fail_under = 92\n", ".lessons_coverage.json": {"measured": 91.9}}, ["coverage-floor"])["findings"]), 1)

    def test_no_floor_no_note(self):
        res = run({"x.py": "pass\n"}, ["coverage-floor"])
        self.assertEqual((res["findings"], res["notes"]), ([], []))


class LangKeys(unittest.TestCase):
    def test_complete_catalog_is_clean(self):
        self.assertEqual(run(CATALOG, ["lang-keys"])["findings"], [])

    def test_missing_key_and_missing_file(self):
        files = dict(CATALOG)
        files["locales/de.json"] = {"k.a": "a"}
        del files["locales/pt.json"]
        res = run(files, ["lang-keys"])
        msgs = sorted((f["file"], f["message"]) for f in res["findings"])
        self.assertEqual(len(msgs), 2)
        self.assertIn("k.b", msgs[0][1])
        self.assertIn("missing file", msgs[1][1])

    def test_nested_keys_underscore_meta_and_optional(self):
        files = {f"locales/{l}.json": {"_author": "x", "a": {"b": "1"}} for l in ll.LANGS}
        self.assertEqual(run(files, ["lang-keys"])["findings"], [])
        files["locales/es.json"] = {"_author": "x", "a": {}}
        self.assertEqual(len(run(files, ["lang-keys"])["findings"]), 1)
        files["locales/en.json"] = {"a": {"b": "1"}, "_optional": ["a.b"]}
        self.assertEqual(run(files, ["lang-keys"])["findings"], [])   # known false positive solved with _optional

    def test_extra_keys_in_other_languages_are_not_flagged(self):
        files = dict(CATALOG)
        files["locales/fr.json"] = {"k.a": "a", "k.b": "b", "k.extra": "x"}
        self.assertEqual(run(files, ["lang-keys"])["findings"], [])

    def test_invalid_json_is_reported_not_crashing(self):
        with Repo(CATALOG) as repo:
            (repo / "locales" / "it.json").write_text("{nope", encoding="utf-8")
            res = ll.lint_repo(repo, ["lang-keys"])
        self.assertEqual(len(res["findings"]), 1)

    def test_a_lone_en_json_elsewhere_is_not_a_catalog(self):
        self.assertEqual(run({"data/en.json": {"x": 1}}, ["lang-keys"])["findings"], [])


class VersionMismatch(unittest.TestCase):
    README = "| Version | `{v}` |\n"

    def files(self, **over):
        base = {"urtc.project.json": {"version": "0.2.6"}, "pyproject.toml": '[project]\nname = "x"\nversion = "0.2.6"\n[tool.other]\nversion = "9.9.9"\n',
                "src/toy/__init__.py": '__version__ = "0.2.6"\n', "README.md": self.README.format(v="0.2.6"),
                "README_jpn.md": "| バージョン | `0.2.6` |\n"}
        base.update(over)
        return base

    def test_consistent_versions_are_clean(self):
        self.assertEqual(run(self.files(), ["version-mismatch"])["findings"], [])

    def test_each_source_can_diverge(self):
        for key, bad in (("src/toy/__init__.py", '__version__ = "0.2.5"\n'), ("README.md", self.README.format(v="0.2.4")),
                         ("README_jpn.md", "| バージョン | `0.1.0` |\n"), ("pyproject.toml", '[project]\nversion = "1.0.0"\n'),
                         ("package.json", {"version": "3.3.3"}), ("Cargo.toml", '[package]\nname = "a"\nversion = "0.9.0"\n[dependencies]\nserde = { version = "1" }\n')):
            res = run(self.files(**{key: bad}), ["version-mismatch"])
            self.assertEqual(len(res["findings"]), 1, key)

    def test_badge_mismatch(self):
        readme = '<img src="https://img.shields.io/badge/Version-0.0.8-0f6cbd.svg" alt="Version">\n' + self.README.format(v="0.2.6")
        res = run(self.files(**{"README.md": readme}), ["version-mismatch"])
        self.assertEqual(len(res["findings"]), 1)
        self.assertIn("0.0.8", res["findings"][0]["message"])

    def test_four_component_versions_and_v_prefix(self):
        files = self.files(**{"urtc.project.json": {"version": "0.8.1.3"}, "pyproject.toml": '[project]\nversion = "v0.8.1.3"\n',
                              "src/toy/__init__.py": '__version__ = "0.8.1.3"\n', "README.md": self.README.format(v="0.8.1.3"), "README_jpn.md": "| バージョン | `0.8.1.3` |\n"})
        self.assertEqual(run(files, ["version-mismatch"])["findings"], [])
        files["README.md"] = self.README.format(v="0.8.1")   # 3 components is not the same as 4
        self.assertEqual(len(run(files, ["version-mismatch"])["findings"]), 1)

    def test_trailing_zero_fourth_component_equals_three_components(self):
        nl = chr(10)
        files = self.files(**{"urtc.project.json": {"version": "0.8.3.0"}, "pyproject.toml": '[project]' + nl + 'version = "0.8.3"' + nl,
                              "src/toy/__init__.py": '__version__ = "0.8.3"' + nl, "README.md": self.README.format(v="0.8.3.0"),
                              "README_jpn.md": "| バージョン | `0.8.3.0` |" + nl})
        self.assertEqual(run(files, ["version-mismatch"])["findings"], [])

    def test_single_source_and_no_sources_are_clean(self):
        self.assertEqual(run({"urtc.project.json": {"version": "1.0.0"}}, ["version-mismatch"])["findings"], [])
        self.assertEqual(run({"a.txt": "x"}, ["version-mismatch"])["findings"], [])

    def test_known_false_positive_table_row_of_another_component(self):
        # documented: if the Version table of the README quotes another component it is reported
        self.assertEqual(len(run(self.files(**{"README.md": self.README.format(v="2.0.0")}), ["version-mismatch"])["findings"]), 1)


class Refinements(unittest.TestCase):
    def test_internal_library_with_its_own_version_is_ignored(self):
        nl = chr(10)
        base = {"urtc.project.json": {"version": "0.5.6"}, "README.md": "| Version | `0.5.6` |" + nl,
                "urtc_can/__init__.py": '__version__ = "0.2.6"' + nl, "src/vision_companion/__init__.py": '__version__ = "0.0.3"' + nl}
        with Repo(base) as repo:
            named = repo.parent / "URTC-FLASHER"
            repo.rename(named)
            self.assertEqual(ll.lint_repo(named, ["version-mismatch"])["findings"], [])
        # the package that carries the name of the repository does count
        base["src/toy/__init__.py"] = '__version__ = "0.1.0"' + nl
        self.assertEqual(len(run(base, ["version-mismatch"])["findings"]), 1)

    def test_is_own_package(self):
        self.assertTrue(ll.is_own_package("URTC-GATEWAY", "urtc_gateway"))
        self.assertTrue(ll.is_own_package("HYDRA-UMC-LOCAL-TECHNICIAN", "hydra_umc_local_technician"))
        self.assertTrue(ll.is_own_package("ARMOR-COMMON", "armor_common"))
        self.assertFalse(ll.is_own_package("URTC-FLASHER", "urtc_can"))
        self.assertFalse(ll.is_own_package("URTC-VISION-TOOL", "vision_companion"))

    def test_coverage_floor_without_saved_measure_never_blocks(self):
        files = {"pyproject.toml": "fail_under = 99" + chr(10)}
        with Repo(files) as repo:
            self.assertEqual(Cli().call("--repo", str(repo), "--check")[0], 0)


SUB = "import subprocess" + chr(10) + "subprocess.run(['a'])" + chr(10)


class BaselineAndConfig(unittest.TestCase):
    CFG = "tools/hygiene_config.json"

    def lint(self, files, **kw):
        with Repo(files) as repo:
            return ll.lint_repo(repo, ll.RULES, config=self.CFG, **kw)

    def test_baseline_counts_per_file_and_only_new_ones_are_new(self):
        two = SUB + "subprocess.run(['b'])" + chr(10)
        with Repo({"a.py": two, "b.py": SUB}) as repo:
            res = ll.lint_repo(repo, ["subprocess-timeout"], config=self.CFG)
            self.assertTrue(all(f["new"] for f in res["findings"]))
            ll.write_baseline(res, repo / ll.DEFAULT_BASELINE)
            res = ll.lint_repo(repo, ["subprocess-timeout"], config=self.CFG)
            self.assertEqual([f["new"] for f in res["findings"]], [False, False, False])
            (repo / "a.py").write_text("import os" + chr(10) + two + "import subprocess" + chr(10) + "subprocess.call(['c'])" + chr(10), encoding="utf-8")   # lines move, one call is added
            res = ll.lint_repo(repo, ["subprocess-timeout"], config=self.CFG)
            self.assertEqual(sorted(f["new"] for f in res["findings"]), [False, False, False, True])
            (repo / "a.py").write_text("pass" + chr(10), encoding="utf-8")   # fixing leaves stale baseline entries
            res = ll.lint_repo(repo, ["subprocess-timeout"], config=self.CFG)
            self.assertEqual(res["resolved"], 2)

    def test_ignore_globs_and_disabled_and_rules_from_config(self):
        cfg = {"lessons_lint": {"ignore": {"subprocess-timeout": ["tools/*.py"]}}}
        res = self.lint({"tools/x.py": SUB, "src/y.py": SUB, self.CFG: cfg})
        self.assertEqual([f["file"] for f in res["findings"]], ["src/y.py"])
        res = self.lint({"src/y.py": SUB, self.CFG: {"lessons_lint": {"enabled": False}}})
        self.assertEqual((res["findings"], res.get("disabled")), ([], True))

    def test_cli_check_write_baseline_and_rules_from_config(self):
        cli = Cli()
        with Repo({"a.py": SUB, "b.json": {}}) as repo:
            self.assertEqual(cli.call("--repo", str(repo), "--check")[0], 1)
            code, out, err = cli.call("--repo", str(repo), "--write-baseline")
            self.assertEqual(code, 0)
            self.assertIn("baseline written", err)
            code, out, _ = cli.call("--repo", str(repo), "--check")
            self.assertEqual(code, 0)
            self.assertIn("LESSONS_LINT=PASS new=0 findings=1", out)
            (repo / "c.py").write_text(SUB, encoding="utf-8")
            self.assertEqual(cli.call("--repo", str(repo), "--check")[0], 1)
            self.assertEqual(cli.call("--repo", str(repo), "--check", "--config", "none")[0], 1)   # the new file is still new; the default baseline is read even without a config
            (repo / "tools" / "hygiene_config.json").write_text(json.dumps({"lessons_lint": {"rules": ["lang-keys"]}}), encoding="utf-8")
            self.assertEqual(cli.call("--repo", str(repo), "--check")[0], 0)   # only lang-keys is enforced


class Cli(unittest.TestCase):
    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ll.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_check_json_and_errors(self):
        with Repo({"x.py": "import subprocess\nsubprocess.run(['a'])\n"}) as repo:
            code, out, _ = self.call("--repo", str(repo), "--check")
            self.assertEqual(code, 1)
            self.assertIn("LESSONS_LINT=FAIL", out)
            code, out, err = self.call("--repo", str(repo), "--json", "--check")
            self.assertEqual(json.loads(out)["findings"][0]["rule"], "subprocess-timeout")
            self.assertEqual(self.call("--repo", str(repo), "--rules", "lang-keys", "--check")[0], 0)
            self.assertEqual(self.call("--repo", str(repo), "--rules", "nope")[0], 2)
        self.assertEqual(self.call("--repo", str(Path(tempfile.gettempdir()) / "no_such_dir_ll"))[0], 2)

    def test_read_only_and_fast_on_a_toy_repo(self):
        files = {f"m{i}.py": "import subprocess\nsubprocess.run(['a'])\n" for i in range(200)}
        with Repo(files) as repo:
            before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
            t0 = time.monotonic()
            self.call("--repo", str(repo))
            self.assertLess(time.monotonic() - t0, 20)
            self.assertEqual(before, {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()})


class CiStep(unittest.TestCase):
    def test_step_does_not_block_without_settings_or_baseline(self):
        with Repo({"a.py": SUB}) as repo:
            self.assertEqual(ll.run_in_ci(repo), [])

    def test_step_blocks_new_findings_after_opting_in(self):
        with Repo({"a.py": SUB, "tools/hygiene_config.json": {"lessons_lint": {"enabled": True}}}) as repo:
            problems = ll.run_in_ci(repo)
            self.assertEqual(len(problems), 2)
            self.assertIn("lessons lint: 1 new", problems[-1])
            ll.write_baseline(ll.lint_repo(repo, ll.RULES, config=ll.CONFIG_FILE), repo / ll.DEFAULT_BASELINE)
            self.assertEqual(ll.run_in_ci(repo), [])
            (repo / "b.py").write_text(SUB, encoding="utf-8")
            self.assertEqual(len(ll.run_in_ci(repo)), 2)

    def test_step_follows_rules_ignore_and_enabled_of_the_settings(self):
        cfg = {"lessons_lint": {"rules": ["lang-keys"]}}
        with Repo({"a.py": SUB, "tools/hygiene_config.json": cfg}) as repo:
            self.assertEqual(ll.run_in_ci(repo), [])
        cfg = {"lessons_lint": {"ignore": {"subprocess-timeout": ["a.py"]}}}
        with Repo({"a.py": SUB, "tools/hygiene_config.json": cfg}) as repo:
            self.assertEqual(ll.run_in_ci(repo), [])
        with Repo({"a.py": SUB, "tools/hygiene_config.json": {"lessons_lint": {"enabled": False}}}) as repo:
            self.assertEqual(ll.run_in_ci(repo), [])


if __name__ == "__main__":
    unittest.main()
