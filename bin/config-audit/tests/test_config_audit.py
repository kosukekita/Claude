from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from os import utime
from pathlib import Path
from unittest.mock import Mock


MODULE_PATH = Path(__file__).parents[1] / "config_audit.py"
SPEC = importlib.util.spec_from_file_location("config_audit", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
config_audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = config_audit
SPEC.loader.exec_module(config_audit)


class ReferenceChecksTest(unittest.TestCase):
    def test_dead_reference_has_source_line_and_failed_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CLAUDE.md"
            source.write_text("first\nSee `missing/tool.sh`\n", encoding="utf-8")

            findings = config_audit.find_dead_refs([source], root)

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.kind, "dead-ref")
        self.assertEqual(finding.location, f"{source}:2")
        self.assertEqual(finding.evidence["line_text"], "See `missing/tool.sh`")
        self.assertEqual(
            finding.evidence["resolved_target"], str(root / "missing/tool.sh")
        )
        self.assertIs(finding.evidence["exists"], False)

    def test_dead_reference_ignores_api_xpath_placeholders_and_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "SKILL.md"
            source.write_text(
                "\n".join(
                    [
                        "API `/api/users/0/items`",
                        "XPath `/body/p[N]`",
                        "model `.../image-to-video`",
                        "format `%.3E`",
                        "example `.env.local`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            findings = config_audit.find_dead_refs([source], root)

        self.assertEqual(findings, [])

    def test_home_reference_is_expanded_before_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir()
            source = claude_dir / "CLAUDE.md"
            source.write_text("See `~/.config/missing.json`\n", encoding="utf-8")

            findings = config_audit.find_dead_refs([source], claude_dir)

        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0].evidence["resolved_target"],
            str(home / ".config/missing.json"),
        )

    def test_linux_ignores_windows_specific_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "SKILL.md"
            source.write_text(
                "Windows CLI: `~/.grok/bin/grok.exe`\n", encoding="utf-8"
            )

            findings = config_audit.find_dead_refs(
                [source], root, platform_name="linux"
            )

        self.assertEqual(findings, [])

    def test_dead_skill_reference_reports_unresolved_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "CLAUDE.md"
            source.write_text(
                "Use **missing-skill** スキル\n", encoding="utf-8"
            )

            findings = config_audit.find_dead_skill_refs(
                [source], {"existing-skill"}
            )

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.kind, "dead-ref")
        self.assertEqual(finding.location, f"{source}:1")
        self.assertEqual(finding.evidence["resolved_name"], "missing-skill")
        self.assertIs(finding.evidence["exists"], False)

    def test_dead_memory_link_reports_missing_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory_dir = Path(tmp)
            source = memory_dir / "one.md"
            source.write_text("See [[not-there]]\n", encoding="utf-8")

            findings = config_audit.find_dead_memlinks(memory_dir)

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.kind, "dead-memlink")
        self.assertEqual(finding.location, f"{source}:1")
        self.assertEqual(
            finding.evidence["resolved_target"], str(memory_dir / "not-there.md")
        )
        self.assertIs(finding.evidence["exists"], False)

    def test_memory_index_reports_both_orphan_directions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory_dir = Path(tmp)
            index = memory_dir / "MEMORY.md"
            index.write_text("- [Missing](missing.md)\n", encoding="utf-8")
            orphan = memory_dir / "orphan.md"
            orphan.write_text("body\n", encoding="utf-8")

            findings = config_audit.find_memory_index_orphans(memory_dir)

        self.assertEqual(
            {finding.target for finding in findings},
            {"missing.md", "orphan.md"},
        )
        for finding in findings:
            self.assertEqual(finding.kind, "mem-index")
            self.assertIn(":", finding.location)
            self.assertIn("check", finding.evidence)


class HookNoopTest(unittest.TestCase):
    def test_linux_ps1_only_hook_is_reported_with_dispatch_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hooks = root / "hooks"
            hooks.mkdir()
            (hooks / "memory-inject.ps1").write_text("noop\n", encoding="utf-8")
            settings = root / "settings.json"
            settings.write_text(
                json.dumps(
                    {
                        "hooks": {
                            "SessionStart": [
                                {
                                    "matcher": "",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": (
                                                'node "$HOME/.claude/hooks/dispatch.js" '
                                                "memory-inject"
                                            ),
                                        }
                                    ],
                                }
                            ]
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            findings = config_audit.find_hook_noops(
                root,
                platform_name="linux",
                command_exists=lambda _command: False,
            )

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.kind, "hook-noop")
        self.assertEqual(finding.target, "memory-inject")
        self.assertRegex(finding.location, rf"^{settings}:[0-9]+$")
        self.assertEqual(
            finding.evidence["candidates"],
            [
                "memory-inject.mjs",
                "memory-inject.cjs",
                "memory-inject.js",
                "memory-inject.sh",
                "memory-inject.py",
                "memory-inject.ps1",
            ],
        )
        self.assertEqual(finding.evidence["available_files"], ["memory-inject.ps1"])
        self.assertEqual(
            finding.evidence["missing_commands"], ["pwsh", "powershell"]
        )


class OperationalChecksTest(unittest.TestCase):
    def test_size_finding_explains_approximation_and_delta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            claude_md = Path(tmp) / "CLAUDE.md"
            claude_md.write_text("abcd" * 1001, encoding="utf-8")

            finding = config_audit.find_size(claude_md, previous_value=900)

        self.assertEqual(finding.kind, "size")
        self.assertEqual(finding.location, str(claude_md))
        self.assertGreater(finding.value, 1000)
        self.assertEqual(finding.evidence["previous_value"], 900)
        self.assertEqual(
            finding.evidence["delta"], finding.value - 900
        )
        self.assertIn("approx", finding.evidence["measurement_method"].lower())

    def test_unused_skill_counts_only_explicit_skill_tool_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            logs = root / "projects"
            (skills / "used").mkdir(parents=True)
            (skills / "unused").mkdir()
            for name in ("used", "unused"):
                (skills / name / "SKILL.md").write_text(
                    f"---\nname: {name}\n---\n", encoding="utf-8"
                )
            logs.mkdir()
            log = logs / "session.jsonl"
            log.write_text(
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "name": "Skill",
                                    "input": {"skill": "used"},
                                }
                            ]
                        }
                    }
                )
                + "\n"
                + json.dumps({"text": "unused skill mentioned in prose"})
                + "\n",
                encoding="utf-8",
            )

            findings = config_audit.find_unused_skills(skills, logs)

        self.assertEqual([finding.target for finding in findings], ["unused"])
        finding = findings[0]
        self.assertEqual(finding.kind, "skill-unused")
        self.assertEqual(finding.evidence["log_files_scanned"], 1)
        self.assertEqual(finding.evidence["explicit_call_count"], 0)
        self.assertEqual(finding.evidence["glob"], "**/*.jsonl")

    def test_failed_unit_uses_verbatim_journal_message(self) -> None:
        entries = [
            {
                "_COMM": "systemd",
                "_SYSTEMD_USER_UNIT": "sample.timer",
                "__REALTIME_TIMESTAMP": "1786400000000000",
                "MESSAGE": "Failed with result 'exit-code'.",
            }
        ]

        findings = config_audit.find_hook_failures(entries)

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.kind, "hook-fail")
        self.assertEqual(finding.target, "sample.timer")
        self.assertEqual(
            finding.evidence["journal_message"], "Failed with result 'exit-code'."
        )
        self.assertIn("failure_time", finding.evidence)

    def test_application_failed_message_is_not_a_unit_failure(self) -> None:
        entries = [
            {
                "_COMM": "python",
                "_SYSTEMD_USER_UNIT": "worker.service",
                "__REALTIME_TIMESTAMP": "1786400000000000",
                "MESSAGE": "model failed to load",
            }
        ]

        self.assertEqual(config_audit.find_hook_failures(entries), [])

    def test_systemd_failed_to_start_uses_named_service_not_init_scope(self) -> None:
        entries = [
            {
                "_COMM": "systemd",
                "_SYSTEMD_USER_UNIT": "init.scope",
                "__REALTIME_TIMESTAMP": "1786400000000000",
                "MESSAGE": "Failed to start actual-job.service - fixture.",
            }
        ]

        findings = config_audit.find_hook_failures(entries)

        self.assertEqual([finding.target for finding in findings], ["actual-job.service"])

    def test_incident_after_all_reflection_files_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            incidents = root / "improvements" / "incidents.jsonl"
            incidents.parent.mkdir()
            incidents.write_text(
                json.dumps({"date": "2026-01-02", "action": "example"}) + "\n",
                encoding="utf-8",
            )
            claude_md = root / "CLAUDE.md"
            claude_md.write_text("rules\n", encoding="utf-8")
            hooks = root / "hooks"
            hooks.mkdir()
            hook = hooks / "guard.py"
            hook.write_text("pass\n", encoding="utf-8")
            before = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
            utime(claude_md, (before, before))
            utime(hook, (before, before))

            findings = config_audit.find_unreflected_incidents(
                incidents, claude_md, hooks
            )

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.kind, "incident-unreflected")
        self.assertEqual(finding.location, f"{incidents}:1")
        self.assertEqual(finding.evidence["incident_date"], "2026-01-02")
        self.assertIn("claude_mtime", finding.evidence)
        self.assertIn("hooks_latest_mtime", finding.evidence)


class StateAndReportTest(unittest.TestCase):
    @staticmethod
    def finding(kind: str, target: str, value: int | None = None):
        return config_audit.Finding(
            kind=kind,
            target=target,
            location=f"/config/{target}:1",
            summary=f"summary {target}",
            evidence={"check": "fixture evidence"},
            value=value,
        )

    def test_same_input_second_comparison_has_no_changes(self) -> None:
        current = [self.finding("dead-ref", "missing")]

        first = config_audit.compare_with_state(
            current, {"version": 1, "findings": {}}, size_change_threshold=50
        )
        second = config_audit.compare_with_state(
            current, first.next_state, size_change_threshold=50
        )

        self.assertEqual(len(first.new_or_changed), 1)
        self.assertTrue(first.should_notify)
        self.assertEqual(second.new_or_changed, [])
        self.assertEqual(second.resolved, [])
        self.assertFalse(second.should_notify)

    def test_resolved_finding_is_reported(self) -> None:
        old = self.finding("dead-ref", "gone")
        previous = config_audit.compare_with_state(
            [old], {"version": 1, "findings": {}}, size_change_threshold=50
        ).next_state

        delta = config_audit.compare_with_state(
            [], previous, size_change_threshold=50
        )

        self.assertEqual(len(delta.resolved), 1)
        self.assertEqual(delta.resolved[0].finding_id, old.finding_id)
        self.assertTrue(delta.should_notify)

    def test_size_repeats_only_at_configured_change_threshold(self) -> None:
        old_size = self.finding("size", "/config/CLAUDE.md", value=1000)
        previous = config_audit.compare_with_state(
            [old_size], {"version": 1, "findings": {}}, size_change_threshold=10
        ).next_state

        small = config_audit.compare_with_state(
            [self.finding("size", "/config/CLAUDE.md", value=1009)],
            previous,
            size_change_threshold=10,
        )
        material = config_audit.compare_with_state(
            [self.finding("size", "/config/CLAUDE.md", value=1010)],
            previous,
            size_change_threshold=10,
        )

        self.assertFalse(small.should_notify)
        self.assertEqual(len(material.new_or_changed), 1)
        self.assertEqual(material.new_or_changed[0].status, "changed")

    def test_skill_unused_report_has_all_caveats_and_forbidden_phrase_absent(self) -> None:
        unused = self.finding("skill-unused", "rare-skill", value=0)
        delta = config_audit.compare_with_state(
            [unused], {"version": 1, "findings": {}}, size_change_threshold=50
        )

        report = config_audit.render_report(delta)

        self.assertIn("明示的な Skill ツール呼び出ししか数えていません", report)
        self.assertIn("Windows機の使用実績は不可視", report)
        self.assertIn("他スキルからの依存・ルーティング先", report)
        self.assertNotIn("削除候補", report)
        self.assertIn("/config/rare-skill:1", report)
        self.assertIn("fixture evidence", report)

    def test_state_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state = {"version": 1, "findings": {"x:y": {"kind": "x"}}}

            config_audit.write_state(state_path, state)
            loaded = config_audit.read_state(state_path)

        self.assertEqual(loaded, state)


class RunAuditTest(unittest.TestCase):
    def make_root(self, base: Path) -> Path:
        root = base / ".claude"
        (root / "hooks").mkdir(parents=True)
        (root / "skills" / "fixture-skill").mkdir(parents=True)
        (root / "projects" / "-home-kita--claude" / "memory").mkdir(
            parents=True
        )
        (root / "improvements").mkdir()
        (root / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")
        (root / "settings.json").write_text(
            json.dumps({"hooks": {}}), encoding="utf-8"
        )
        (root / "hooks" / "dispatch.js").write_text(
            "// fixture\n", encoding="utf-8"
        )
        (root / "skills" / "fixture-skill" / "SKILL.md").write_text(
            "---\nname: fixture-skill\n---\n", encoding="utf-8"
        )
        (
            root
            / "projects"
            / "-home-kita--claude"
            / "memory"
            / "MEMORY.md"
        ).write_text("", encoding="utf-8")
        (root / "improvements" / "incidents.jsonl").write_text(
            "", encoding="utf-8"
        )
        return root

    def test_dry_run_persists_state_and_report_but_never_calls_mailer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            output = base / "media-out" / "config-audit"
            mailer = Mock(side_effect=AssertionError("mailer called in dry-run"))

            first = config_audit.run_audit(
                claude_dir=root,
                output_dir=output,
                size_change_threshold=50,
                dry_run=True,
                journal_entries=[],
                mailer=mailer,
            )
            second = config_audit.run_audit(
                claude_dir=root,
                output_dir=output,
                size_change_threshold=50,
                dry_run=True,
                journal_entries=[],
                mailer=mailer,
            )

        self.assertTrue(first.delta.should_notify)
        self.assertFalse(second.delta.should_notify)
        self.assertIn("新規・変更: 0 / 解消: 0", second.report)
        self.assertTrue(first.report_path.name.startswith("report-"))
        self.assertFalse(mailer.called)

    def test_non_dry_run_sends_only_when_delta_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            output = base / "media-out" / "config-audit"
            mailer = Mock()

            config_audit.run_audit(
                claude_dir=root,
                output_dir=output,
                size_change_threshold=50,
                dry_run=False,
                journal_entries=[],
                mailer=mailer,
            )
            config_audit.run_audit(
                claude_dir=root,
                output_dir=output,
                size_change_threshold=50,
                dry_run=False,
                journal_entries=[],
                mailer=mailer,
            )

        self.assertEqual(mailer.call_count, 1)

    def test_missing_config_root_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            exit_code = config_audit.main(
                ["--dry-run", "--claude-dir", str(missing)]
            )

        self.assertNotEqual(exit_code, 0)

    def test_audit_does_not_modify_any_input_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            inputs = sorted(path for path in root.rglob("*") if path.is_file())
            before = {
                path: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in inputs
            }

            config_audit.run_audit(
                claude_dir=root,
                output_dir=base / "output",
                size_change_threshold=50,
                dry_run=True,
                journal_entries=[],
            )

            after = {
                path: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in inputs
            }

        self.assertEqual(after, before)


class PackagingTest(unittest.TestCase):
    ROOT = Path(__file__).parents[1]

    def test_config_exposes_size_change_threshold(self) -> None:
        config = json.loads((self.ROOT / "config.json").read_text(encoding="utf-8"))

        self.assertIsInstance(config["size_change_threshold"], int)
        self.assertGreater(config["size_change_threshold"], 0)

    def test_mail_message_id_uses_real_domain(self) -> None:
        source = (self.ROOT / "send_mail.mjs").read_text(encoding="utf-8")

        self.assertRegex(source, r"Message-ID:.*@gmail\.com")
        self.assertNotIn(".local>", source)
        self.assertIn("smtps://smtp.gmail.com:465", source)

    def test_no_llm_api_or_cli_call_exists_in_production_sources(self) -> None:
        sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(self.ROOT.rglob("*"))
            if path.is_file()
            and "tests" not in path.parts
            and path.suffix in {".py", ".mjs", ".json", ".sh", ".service", ".timer"}
        ).lower()
        forbidden = [
            "api.openai.com",
            "api.anthropic.com",
            "localhost:11434",
            "/v1/chat/completions",
            "ollama run",
            "codex exec",
            "claude -p",
        ]

        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, sources)

    def test_timer_is_weekly_persistent_and_avoids_known_busy_hours(self) -> None:
        timer = (self.ROOT / "systemd" / "config-audit.timer").read_text(
            encoding="utf-8"
        )

        self.assertRegex(timer, r"OnCalendar=(Sun|Tue|Wed|Thu|Fri|Sat) ")
        self.assertIn("Persistent=true", timer)
        self.assertNotRegex(timer, r"OnCalendar=.* (06|09|20):")

    def test_installer_is_idempotent_and_enables_timer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            destination = base / "systemd-user"
            fake_bin = base / "bin"
            fake_bin.mkdir()
            calls = base / "systemctl-calls.txt"
            fake_systemctl = fake_bin / "systemctl"
            fake_systemctl.write_text(
                "#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$CALLS_FILE\"\n",
                encoding="utf-8",
            )
            fake_systemctl.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:/usr/bin:/bin"
            environment["CALLS_FILE"] = str(calls)
            environment["CONFIG_AUDIT_SYSTEMD_USER_DIR"] = str(destination)
            installer = self.ROOT / "systemd" / "install.sh"

            for _ in range(2):
                completed = subprocess.run(
                    ["bash", str(installer)],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            installed = sorted(path.name for path in destination.iterdir())
            call_lines = calls.read_text(encoding="utf-8").splitlines()

        self.assertEqual(
            installed, ["config-audit.service", "config-audit.timer"]
        )
        self.assertEqual(call_lines.count("--user daemon-reload"), 2)
        self.assertEqual(
            call_lines.count("--user enable --now config-audit.timer"), 2
        )


if __name__ == "__main__":
    unittest.main()
