"""tools/status_lights.py: the ceiling of every light of the Project status table, from the manifest and the files of the repository, and the HYDRA-UMC origin of the lights (data/glance.json)."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[3] / "tools" / "status_lights.py"
spec = importlib.util.spec_from_file_location("status_lights", TOOL)
status_lights = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status_lights)

G, Y, O, R = status_lights.GREEN, status_lights.YELLOW, status_lights.ORANGE, status_lights.RED
NAMES = ("README.md", "README_spa.md", "README_fra.md", "README_ita.md", "README_deu.md", "README_zho.md", "README_jpn.md", "README_por.md")


def readme(lights, word="Hardware") -> str:
    rows = [("Software", lights[0]), ("Tests", lights[1]), (word, lights[2]), ("Integration", lights[3]), ("Documentation", lights[4])]
    body = "\n".join(f"| {label} | {light} | A sentence that stays, with a | not at the end. |" for label, light in rows)
    return f"# X\n\n## \U0001F6A6 Project status\n\nlegend\n\n| Area | State | What it means |\n|---|---|---|\n{body}\n\n## Overview\n\ntext\n"


def make_repo(root: Path, lights, maturity="established", evidence="bench", extra=None, tests=True, ci=True) -> Path:
    repo = root / "ARMOR-TEST"
    repo.mkdir()
    manifest = {"name": "ARMOR-TEST", "maturity": maturity, "evidence": evidence}
    manifest.update(extra or {})
    (repo / "armor.project.json").write_text(json.dumps(manifest), encoding="utf-8")
    for name in NAMES:
        (repo / name).write_bytes(readme(lights).encode("utf-8"))
    if tests:
        (repo / "tests").mkdir()
        (repo / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
    if ci:
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")
    return repo


class Kinds(unittest.TestCase):
    def test_kind_of_a_label(self):
        self.assertEqual(status_lights.kind_of("Real hardware"), "hardware")
        self.assertEqual(status_lights.kind_of("Hardware"), "hardware")
        self.assertEqual(status_lights.kind_of("Integration"), "integration")
        self.assertEqual(status_lights.kind_of("Tests"), "tests")
        self.assertEqual(status_lights.kind_of("Documentation"), "docs")
        self.assertEqual(status_lights.kind_of("Software"), "software")
        self.assertEqual(status_lights.kind_of("Security"), "other")


class Ceilings(unittest.TestCase):
    def test_evidence_limits_hardware_and_integration(self):
        for evidence, top in (("none", O), ("host-test", O), ("simulator", O), ("bench", Y), ("field", G)):
            self.assertEqual(status_lights.ceiling("hardware", {"evidence": evidence}, True, True, "unknown")[0], top, evidence)
            self.assertEqual(status_lights.ceiling("integration", {"evidence": evidence}, True, True, "unknown")[0], top, evidence)

    def test_evidence_does_not_limit_software(self):
        self.assertEqual(status_lights.ceiling("software", {"evidence": "none"}, True, True, "green")[0], G)

    def test_a_repository_without_hardware_is_not_limited_by_evidence(self):
        self.assertEqual(status_lights.ceiling("integration", {"evidence": "host-test", "hardware_bound": False}, True, True, "unknown")[0], G)

    def test_software_tests_docs_need_tests_and_a_ci(self):
        for kind in ("software", "tests", "docs"):
            self.assertEqual(status_lights.ceiling(kind, {}, False, True, "green")[0], Y)
            self.assertEqual(status_lights.ceiling(kind, {}, True, False, "green")[0], Y)
            self.assertEqual(status_lights.ceiling(kind, {}, True, True, "red")[0], Y)
            self.assertEqual(status_lights.ceiling(kind, {}, True, True, "green")[0], G)

    def test_low_maturity_limits_everything_to_yellow(self):
        for maturity in ("scaffolding", "experimental", "alpha"):
            for kind in ("software", "tests", "docs", "hardware", "other"):
                self.assertEqual(status_lights.ceiling(kind, {"maturity": maturity, "evidence": "field"}, True, True, "green")[0], Y)


class Check(unittest.TestCase):
    def test_a_false_green_fails_the_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            problems = status_lights.run_in_ci(repo)
            self.assertEqual(len(problems), 2)
            self.assertTrue(any("Hardware" in p for p in problems) and any("Integration" in p for p in problems))

    def test_lights_within_the_ceilings_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, Y, Y, G], evidence="bench")
            self.assertEqual(status_lights.run_in_ci(repo), [])

    def test_a_missing_or_unknown_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G])
            manifest = repo / "armor.project.json"
            manifest.write_text(json.dumps({"name": "x", "maturity": "established"}), encoding="utf-8")
            self.assertTrue(any("no 'evidence'" in p for p in status_lights.run_in_ci(repo)))
            manifest.write_text(json.dumps({"name": "x", "maturity": "established", "evidence": "magic"}), encoding="utf-8")
            self.assertTrue(any("magic" in p for p in status_lights.run_in_ci(repo)))

    def test_translations_with_other_lights_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G])
            (repo / "README_por.md").write_bytes(readme([G, G, R, O, G]).encode("utf-8"))
            self.assertTrue(any("README_por.md" in p for p in status_lights.run_in_ci(repo)))

    def test_no_tests_caps_the_software_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G], tests=False)
            self.assertEqual(len(status_lights.run_in_ci(repo)), 3)


class Apply(unittest.TestCase):
    def test_apply_lowers_only_the_light_in_the_eight_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="simulator")
            before = (repo / "README.md").read_text(encoding="utf-8")
            self.assertEqual(status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"]), 0)
            for name in NAMES:
                after = (repo / name).read_text(encoding="utf-8")
                self.assertEqual(after, readme([G, G, O, O, G]))
            self.assertEqual(before.replace(G, "").replace(O, ""), (repo / "README.md").read_text(encoding="utf-8").replace(G, "").replace(O, ""))
            self.assertEqual(status_lights.run_in_ci(repo), [])

    def test_apply_never_raises_without_the_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [Y, Y, R, R, Y], evidence="field")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((repo / "README.md").read_text(encoding="utf-8"), readme([Y, Y, R, R, Y]))
            status_lights.main(["--apply", "--raise", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((repo / "README.md").read_text(encoding="utf-8"), readme([Y, Y, O, O, Y]))

    def test_apply_keeps_line_endings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            for name in NAMES:
                path = repo / name
                path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            data = (repo / "README.md").read_bytes()
            self.assertEqual(data.count(b"\r\n"), data.count(b"\n"))

    def test_apply_patches_the_source_of_the_armor_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            source = Path(tmp) / "ARMOR-DOCS" / "tools" / "readme_src" / "repos"
            source.mkdir(parents=True)
            text = 'FACTS = {\n  "status": [\n    [\n      "software",\n      "green",\n    ],\n    [\n      "tests",\n      "green",\n    ],\n    [\n      "hardware",\n      "green",\n    ],\n    [\n      "integration",\n      "green",\n    ],\n    [\n      "docs",\n      "green",\n    ],\n  ],\n}\n'
            (source / "ARMOR_TEST.py").write_text(text, encoding="utf-8")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((source / "ARMOR_TEST.py").read_text(encoding="utf-8"), text.replace('"hardware",\n      "green"', '"hardware",\n      "orange"').replace('"integration",\n      "green"', '"integration",\n      "orange"'))

    def test_apply_patches_the_sections_of_the_urtc_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            repo = repo.rename(Path(tmp) / "URTC-TEST")
            spec = Path(tmp) / "URTC-COMMON" / "spec" / "readme"
            spec.mkdir(parents=True)
            body = readme([G, G, G, G, G]).split("\n## Overview")[0].split("legend\n\n", 1)[1]
            data = {"sections": [{"id": "status_test", "repos": ["URTC-TEST"], "body": {"english": body, "spanish": body}}]}
            (spec / "sections.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            after = json.loads((spec / "sections.json").read_text(encoding="utf-8"))
            for text in after["sections"][0]["body"].values():
                self.assertEqual(text, body.replace("| Hardware | " + G, "| Hardware | " + O).replace("| Integration | " + G, "| Integration | " + O))

    def test_suggest_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [Y, Y, R, R, Y], evidence="field")
            before = (repo / "README.md").read_bytes()
            self.assertEqual(status_lights.main(["--suggest", "--repo", str(repo), "--ci", "off"]), 0)
            self.assertEqual(before, (repo / "README.md").read_bytes())


def hydra_repo(root: Path, lights, hardware: str, manifest_extra: dict, name="HYDRA-UMC-TEST") -> Path:
    """A repository of the HYDRA-UMC family next to a HYDRA-UMC-DOCS that holds data/glance.json."""
    repo = make_repo(root, lights, evidence=manifest_extra.pop("evidence", "none"), extra=manifest_extra)
    repo = repo.rename(root / name)
    (repo / "armor.project.json").rename(repo / "hydra-umc.project.json")
    data = root / "HYDRA-UMC-DOCS" / "data"
    data.mkdir(parents=True)
    (data / "glance.json").write_text(json.dumps({"repos": {name: {"hardware": hardware, "target": "board", "tests": {"count": 3, "command": "x"}}}}), encoding="utf-8")
    return repo


class HydraOrigin(unittest.TestCase):
    def test_the_evidence_must_agree_with_the_hardware_of_glance_json(self):
        for hardware, evidence in (("not_run", "none"), ("not_run", "host-test"), ("simulated", "simulator"), ("bench", "bench"), ("in_use", "field")):
            with tempfile.TemporaryDirectory() as tmp:
                repo = hydra_repo(Path(tmp), [O, G, O, O, G], hardware, {"evidence": evidence})
                self.assertEqual(status_lights.run_in_ci(repo), [], (hardware, evidence))

    def test_an_evidence_that_disagrees_with_glance_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [O, G, O, O, G], "bench", {"evidence": "simulator"})
            problems = status_lights.run_in_ci(repo)
            self.assertTrue(any("glance.json holds hardware 'bench'" in p for p in problems), problems)

    def test_not_applicable_needs_hardware_bound_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [G, G, G, G, G], "not_applicable", {"evidence": "none"})
            self.assertTrue(any("hardware_bound" in p for p in status_lights.run_in_ci(repo)))
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [G, G, G, G, G], "not_applicable", {"evidence": "none", "hardware_bound": False})
            self.assertEqual(status_lights.run_in_ci(repo), [])

    def test_hardware_bound_false_with_a_hardware_statement_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [O, G, O, O, G], "simulated", {"evidence": "simulator", "hardware_bound": False})
            self.assertTrue(any("hardware_bound false" in p for p in status_lights.run_in_ci(repo)))

    def test_without_glance_json_next_to_the_repository_only_the_ceilings_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [O, G, O, O, G], "bench", {"evidence": "simulator"})
            (repo.parent / "HYDRA-UMC-DOCS" / "data" / "glance.json").unlink()
            self.assertEqual(status_lights.run_in_ci(repo), [])

    def test_apply_writes_nothing_in_a_hydra_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [G, G, G, G, G], "not_run", {"evidence": "none"})
            before = {name: (repo / name).read_bytes() for name in NAMES}
            self.assertEqual(status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"]), 0)
            self.assertEqual(before, {name: (repo / name).read_bytes() for name in NAMES})

    def test_the_lights_of_a_hydra_repository_above_the_ceiling_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = hydra_repo(Path(tmp), [G, G, G, G, G], "not_run", {"evidence": "none"})
            self.assertEqual(len(status_lights.run_in_ci(repo)), 2)


if __name__ == "__main__":
    unittest.main()
