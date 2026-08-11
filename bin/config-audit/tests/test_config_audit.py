from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "config_audit.py"
SPEC = importlib.util.spec_from_file_location("config_audit", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
config_audit = importlib.util.module_from_spec(SPEC)
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


if __name__ == "__main__":
    unittest.main()
