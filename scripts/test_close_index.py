#!/usr/bin/env python3
"""Checks for close-report indexing and merge eligibility."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_index  # noqa: E402


def main() -> None:
    reports = sorted(
        (build_index.parse_report(p) for p in (ROOT / "archive").rglob("*.html")),
        key=lambda r: r["sort_key"],
        reverse=True,
    )
    kinds = {(r["date"], r["kind"]) for r in reports}
    assert ("2026-09-21", "close") in kinds, kinds
    assert ("2026-09-22", "open") in kinds, kinds
    assert sum(1 for r in reports if r["kind"] == "close" and r["date"] == "2026-09-21") == 1

    close21 = next(r for r in reports if r["kind"] == "close" and r["date"] == "2026-09-21")
    text = close21["path"].read_text(encoding="utf-8")
    assert text.count("<tr><td>科技</td>") + text.count("<tr><td>油气</td>") + text.count("<tr><td>煤炭</td>") + text.count("<tr><td>电力电网</td>") + text.count("<tr><td>农业</td>") + text.count("<tr><td>医药</td>") + text.count("<tr><td>计算机</td>") + text.count("<tr><td>化工</td>") + text.count("<tr><td>金融</td>") == 29, "sector rows must be 29"

    html_index = build_index.render_index(reports)
    assert "收盘对照" in html_index
    assert "收盘报告" in html_index
    assert "最新早报" in html_index
    assert "最新收盘" in html_index
    assert "latest-close.html" in html_index

    latest_open = next(r for r in reports if r["kind"] == "open")
    assert latest_open["date"] == "2026-09-22"
    latest_close = next(r for r in reports if r["kind"] == "close")
    assert latest_close["date"] == "2026-09-22"
    page = build_index.render_latest(latest_open, empty="暂无早报", jumping="跳转到最新早报")
    assert "2026-09-22_0830.html" in page
    assert "2026-09-21_1510.html" not in page

    script = ROOT / "scripts" / "briefing_pr_eligible.sh"
    def eligible(title: str, *files: str) -> int:
        proc = subprocess.run(
            ["bash", str(script), title, *files],
            env={"REPORT_DATE": "2026-09-21"},
            capture_output=True,
            text=True,
        )
        return proc.returncode

    assert eligible("docs: A股收盘对照 2026-09-21", "archive/2026/09/x.html", "latest-close.html") == 0
    assert eligible("docs: A股开盘前早报 2026-09-21", "archive/2026/09/x.html", "latest.html") == 0
    assert eligible("docs: A股收盘对照 2026-09-21", "README.md") == 1
    assert eligible("docs: 只改提示词 2026-09-21", "archive/2026/09/x.html") == 1
    print("ok")


if __name__ == "__main__":
    main()
