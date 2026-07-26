#!/usr/bin/env python3
"""Merge persisted LLM verdicts into a citecheck result without CLI payloads."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def unresolved_count(data: dict[str, Any]) -> int:
    return len(data.get("critical", [])) + sum(
        item.get("llm_verdict") != "pass" for item in data.get("sample", [])
    )


def merge(machine_path: Path, verdict_dir: Path, prefix: str, count: int) -> dict[str, Any]:
    data = json.loads(machine_path.read_text(encoding="utf-8"))
    verdicts: dict[str, dict[str, Any]] = {}
    for index in range(count):
        path = verdict_dir / f"{prefix}-{index}.json"
        verdict = json.loads(path.read_text(encoding="utf-8"))
        pair_id = str(verdict["pair_id"])
        if pair_id in verdicts:
            raise ValueError(f"duplicate pair_id: {pair_id}")
        verdicts[pair_id] = verdict

    sample_ids = {str(item["pair_id"]) for item in data.get("sample", [])}
    if set(verdicts) != sample_ids:
        raise ValueError("persisted verdict IDs do not match the deterministic sample")

    data["sample"] = [
        {
            **pair,
            "llm_verdict": "pass" if verdicts[str(pair["pair_id"])]["verdict"] == "supported" else "fail",
            "llm_reason": verdicts[str(pair["pair_id"])]["reason"],
            "repair": verdicts[str(pair["pair_id"])]["repair"],
        }
        for pair in data.get("sample", [])
    ]
    data["critical"] = [{**item, "resolved": False} for item in data.get("critical", [])]
    return data


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", required=True)
    parser.add_argument("--verdict-dir", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--count", required=True, type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    data = merge(Path(args.machine), Path(args.verdict_dir), args.prefix, args.count)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unresolved = unresolved_count(data)
    print(json.dumps({"written": output.as_posix(), "unresolved": unresolved}))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
