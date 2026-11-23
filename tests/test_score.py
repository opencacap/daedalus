import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "plugins/daedalus-core/evals/score.py"


def finding(tag, location, verifier="CONFIRMED"):
    return (
        f"**{tag} — Something is wrong**\n"
        f"- Location: `{location}`\n"
        "- Lenses: correctness-a\n"
        "- Code: `x`\n"
        "- Failure: it breaks.\n"
        "- Fix: fix it.\n"
        + (f"- Verifier: {verifier} — `{location}` shows it.\n" if verifier else "")
    )


def report(introduced=(), needs_human=(), pre_existing=(), lenses="correctness-a, correctness-b"):
    verdict = "BLOCKING" if any(f.startswith(("**C", "**H")) for f in introduced) else "NOT BLOCKING"
    return (
        "## Code review: `main`...HEAD\n\n"
        f"**Verdict: {verdict}** — reason.\n\n"
        "### Introduced by this diff\n\n" + ("\n".join(introduced) or "None.") + "\n\n"
        "### Needs a human\n\n" + ("\n".join(needs_human) or "None.") + "\n\n"
        "### Pre-existing\n\n" + ("\n".join(pre_existing) or "None.") + "\n\n"
        "### Spec coverage\n\nNo spec available.\n\n"
        "### Checks\n\nNo checks configured.\n\n"
        f"### Summary\n\nLenses run: {lenses}. Lenses skipped: none. Findings: none.\n"
    )


class Results:
    """Builds an aggregate-result.json with one trace file per run."""

    def __init__(self, root, name):
        self.dir = Path(root) / name
        self.dir.mkdir()
        self.cases = []

    def case(self, name, *runs):
        arms = []
        for index, run in enumerate(runs):
            trace = self.dir / f"{name}-{index}.jsonl"
            events = [{"type": "result", "result": "Finders are still running."}]
            for agent_id in run.get("workflow_agents", []):
                progress = [{"type": "workflow_phase", "index": 1, "title": "Find"}]
                agent = {"type": "workflow_agent", "state": "queued"}
                if agent_id is not None:  # a queued agent has no id yet
                    agent.update(agentId=agent_id, state="done")
                progress.append(agent)
                events.append({"type": "system", "subtype": "task_progress", "workflow_progress": progress})
            if run.get("report") is not None:
                events.append(
                    {
                        "type": "result",
                        "result": run["report"],
                        "subagent_stats": {"spawned": run.get("spawned", 10)},
                    }
                )
            trace.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
            arm = {
                "score": 1 if run.get("passed", True) else 0.5,
                "passed": run.get("passed", True),
                "costUsd": run.get("cost", 1.0),
                "durationSeconds": run.get("seconds", 100),
                "tracePath": trace.name,
            }
            arms.append({key: value for key, value in arm.items() if value is not None})
        self.cases.append({"name": name, "arms": {"with": arms}})
        return self

    def write(self):
        path = self.dir / "aggregate-result.json"
        path.write_text(json.dumps({"schemaVersion": 1, "cases": self.cases}), encoding="utf-8")
        return path


def score(labels, *configs, extra=("--json",)):
    with tempfile.TemporaryDirectory() as tmp:
        labels_path = Path(tmp) / "labels.json"
        labels_path.write_text(json.dumps({"cases": labels}), encoding="utf-8")
        args = [f"{name}={path}" for name, path in configs]
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--labels", str(labels_path), *args, *extra],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    return result


def score_json(labels, *configs):
    result = score(labels, *configs)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


SEEDED = {"defects": [{"file": "src/stats.py", "lines": [13, 13], "severity": "CH"}]}


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_seeded_defect_found_at_its_line_counts_toward_ch_recall_and_precision(self):
        results = Results(self.root, "skill").case(
            "seeded-bug",
            {"report": report(introduced=[finding("H1", "src/stats.py:13")])},
            {"report": report()},
        )

        output = score_json({"seeded-bug": SEEDED}, ("skill", results.write()))

        self.assertEqual(output["skill"]["ch_recall"], 0.5)
        self.assertEqual(output["skill"]["precision"], 1.0)

    def test_an_unlabelled_finding_lowers_precision_and_a_low_grade_misses_ch_recall(self):
        results = Results(self.root, "skill").case(
            "seeded-bug",
            {
                "report": report(
                    introduced=[finding("M1", "src/stats.py:12-14"), finding("L1", "src/other.py:3")]
                )
            },
        )

        output = score_json({"seeded-bug": SEEDED}, ("skill", results.write()))

        self.assertEqual(output["skill"]["ch_recall"], 0.0)
        self.assertEqual(output["skill"]["precision"], 0.5)

    def test_a_blocking_verdict_on_a_clean_case_is_a_false_positive(self):
        results = Results(self.root, "skill").case(
            "clean-change",
            {"report": report(introduced=[finding("H1", "src/stats.py:9")])},
            {"report": report()},
            {"report": report(introduced=[finding("L1", "src/stats.py:9")])},
            {"report": report()},
        )

        output = score_json({"clean-change": {"clean": True}}, ("skill", results.write()))

        self.assertEqual(output["skill"]["clean_fp_rate"], 0.25)
        self.assertEqual(output["skill"]["precision"], 0.0)
        self.assertIsNone(output["skill"]["ch_recall"])

    def test_a_defect_without_lines_matches_any_line_of_its_file(self):
        results = Results(self.root, "skill").case(
            "spec",
            {"report": report(introduced=[finding("M1", "src/discounts.py:9"), finding("L1", "src/other.py:9")])},
        )
        labels = {"spec": {"defects": [{"file": "src/discounts.py", "severity": "M"}]}}

        output = score_json(labels, ("skill", results.write()))

        self.assertEqual(output["skill"]["precision"], 0.5)

    def test_run_to_run_variance_spreads_recall_by_run_and_names_flaky_cases(self):
        hit = {"report": report(introduced=[finding("H1", "src/stats.py:13")])}
        miss = {"report": report(), "passed": False}
        security_hit = {"report": report(introduced=[finding("C1", "src/users.py:7")])}
        results = (
            Results(self.root, "skill")
            .case("seeded-bug", hit, miss, hit)
            .case("security", security_hit, security_hit, security_hit)
        )
        labels = {
            "seeded-bug": SEEDED,
            "security": {"defects": [{"file": "src/users.py", "lines": [7, 7], "severity": "CH"}]},
        }

        output = score_json(labels, ("skill", results.write()))

        self.assertEqual(output["skill"]["ch_recall_stdev"], 0.2357)
        self.assertEqual(output["skill"]["pass_rate"], 0.8333)
        self.assertEqual(output["skill"]["flaky_cases"], ["seeded-bug"])

    def test_compliance_needs_every_required_lens_a_verdict_per_finding_and_enough_sub_agents(self):
        lenses = "correctness-a, correctness-b, security"
        found = [finding("H1", "src/stats.py:13")]
        results = Results(self.root, "skill").case(
            "seeded-bug",
            {"report": report(introduced=found, lenses=lenses), "spawned": 4},
            {"report": report(introduced=found, lenses="correctness-a, correctness-b"), "spawned": 4},
            {"report": report(introduced=[finding("H1", "src/stats.py:13", verifier=None)], lenses=lenses), "spawned": 4},
            {"report": report(introduced=found, lenses=lenses), "spawned": 3},
        )
        labels = {"seeded-bug": {**SEEDED, "lenses": ["correctness-a", "correctness-b", "security"]}}

        output = score_json(labels, ("skill", results.write()))

        self.assertEqual(output["skill"]["compliance"], 0.25)
        self.assertEqual(output["skill"]["noncompliant_cases"], ["seeded-bug"])

    def test_workflow_agents_count_as_sub_agents_once_each(self):
        found = [finding("H1", "src/stats.py:13")]
        results = Results(self.root, "workflow").case(
            "seeded-bug",
            {"report": report(introduced=found), "spawned": 0, "workflow_agents": [None, "a", "b", "a", "c"]},
            {"report": report(introduced=found), "spawned": 0, "workflow_agents": ["a", "b", "b", None]},
        )

        output = score_json({"seeded-bug": SEEDED}, ("workflow", results.write()))

        self.assertEqual(output["workflow"]["compliance"], 0.5)

    def test_cost_and_wall_time_average_the_scored_reviews_only(self):
        results = (
            Results(self.root, "skill")
            .case("seeded-bug", {"report": report(), "cost": 1.0, "seconds": 100}, {"report": report(), "cost": 3.0, "seconds": 200})
            .case("bad-ref", {"report": "Review stopped: base ref `x` does not resolve.", "cost": 0.1, "seconds": 5})
        )
        untimed = Results(self.root, "untimed").case("seeded-bug", {"report": report(), "cost": None, "seconds": None})

        output = score_json({"seeded-bug": SEEDED}, ("skill", results.write()), ("untimed", untimed.write()))

        self.assertEqual(output["skill"]["cost_per_review"], 2.0)
        self.assertEqual(output["skill"]["wall_seconds"], 150.0)
        self.assertIsNone(output["untimed"]["cost_per_review"])
        self.assertIsNone(output["untimed"]["wall_seconds"])

    def test_a_missing_trace_stops_the_scorer_with_its_path(self):
        results = Results(self.root, "skill").case("seeded-bug", {"report": report()})
        path = results.write()
        trace = results.dir / "seeded-bug-0.jsonl"
        trace.unlink()

        result = score({"seeded-bug": SEEDED}, ("skill", path))

        self.assertEqual(result.returncode, 2)
        self.assertIn(f"trace not found: {trace}", result.stderr)

    def test_a_configuration_needs_a_name_and_one_results_path(self):
        path = Results(self.root, "skill").case("seeded-bug", {"report": report()}).write()

        unnamed = score({"seeded-bug": SEEDED}, ("", path))
        twice = score({"seeded-bug": SEEDED}, ("skill", path), ("skill", path))

        self.assertEqual(unnamed.returncode, 2)
        self.assertIn("expected NAME=RESULTS", unnamed.stderr)
        self.assertEqual(twice.returncode, 2)
        self.assertIn("configuration skill given twice", twice.stderr)

    def test_a_results_directory_reads_its_aggregate_result(self):
        results = Results(self.root, "skill").case(
            "seeded-bug", {"report": report(introduced=[finding("H1", "src/stats.py:13")])}
        )
        results.write()

        output = score_json({"seeded-bug": SEEDED}, ("skill", results.dir))

        self.assertEqual(output["skill"]["ch_recall"], 1.0)

    def test_the_default_output_is_a_markdown_table_with_one_row_per_configuration(self):
        results = Results(self.root, "skill").case(
            "seeded-bug",
            {"report": report(introduced=[finding("H1", "src/stats.py:13")]), "cost": 1.0, "seconds": 100},
            {"report": report(), "cost": 3.0, "seconds": 200, "passed": False},
        )

        result = score({"seeded-bug": SEEDED}, ("skill", results.write()), extra=())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "| Config | C/H recall | Recall stdev | Precision | Clean FP rate | Pass rate | Compliance | Cost/review (USD) | Wall time (s) |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| skill | 0.50 | 0.50 | 1.00 | n/a | 0.50 | 1.00 | 2.00 | 150 |",
                "",
                "- skill: flaky cases: seeded-bug; non-compliant cases: none",
            ],
        )


if __name__ == "__main__":
    unittest.main()
