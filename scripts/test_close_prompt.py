#!/usr/bin/env python3
"""Alignment and indexing checks for the A-share close briefing prompt."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_index  # noqa: E402

SECTOR_RE = re.compile(r"\b(\d{6})\b")
REQUIRED_HEADINGS = [
    "一、运行判断",
    "二、数据原则",
    "三、报告结构",
    "四、固定跟踪板块",
    "五、HTML交付",
    "六、交付方式",
    "七、写入 GitHub 仓库",
    "八、排版与解读增量",
    "九、知识星球分享文案",
]
FIXED_CODES = [
    "881270",
    "881122",
    "886042",
    "881172",
    "886073",
    "886088",
    "885959",
    "885908",
    "886054",
    "886009",
    "886033",
    "881107",
    "881105",
    "881278",
    "881145",
    "881103",
    "884010",
    "881101",
    "881102",
    "881143",
    "885927",
    "881142",
    "399441",
    "881140",
    "881271",
    "881272",
    "881108",
    "881109",
    "881283",
]


def extract_paste(text: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "开始复制")
    end = next(i for i, line in enumerate(lines) if line.strip() == "结束复制")
    return "\n".join(lines[start + 1 : end])


def extract_section(text: str, start: str, end: str) -> str:
    a = text.index(start)
    b = text.index(end, a + len(start))
    return text[a:b]


def test_prompt_alignment() -> None:
    preopen = (ROOT / "prompts/automation-dashboard-prompt.md").read_text(encoding="utf-8")
    close = (ROOT / "prompts/close-automation-dashboard-prompt.md").read_text(encoding="utf-8")
    canonical = (ROOT / "prompts/ashare-close-briefing.md").read_text(encoding="utf-8")
    paste = extract_paste(close)

    for heading in REQUIRED_HEADINGS:
        assert heading in paste, heading
        assert heading in canonical, heading

    preopen_codes = SECTOR_RE.findall(extract_section(preopen, "四、固定跟踪板块", "五、HTML交付"))
    close_codes = SECTOR_RE.findall(extract_section(paste, "四、固定跟踪板块", "五、HTML交付"))
    assert preopen_codes == close_codes == FIXED_CODES, (preopen_codes, close_codes)
    assert len(close_codes) == 29

    assert "08:30" in preopen
    assert "18:00" in paste
    assert "任务在18:00启动" in paste
    assert "15:10" not in paste
    assert "0 10 * * 1-5" in close
    assert "20 7 * * 1-5" not in close
    assert "A股收盘报告_YYYY-MM-DD_1800.html" in paste
    assert "latest-close.html" in paste
    assert "当日A股复盘" in paste
    assert "08:30至18:00" in paste
    assert "十、早盘信息—收盘验证总览" in paste
    assert "十一、早盘与收盘统一的章节重点条" in paste
    assert "15:00收盘价可以使用" in paste
    assert "不要把它贴进" in close or "不要把它贴进" in close[:800]
    assert "兑现" in paste and "证伪" in paste
    assert "知识星球分享文案" in paste
    assert "881107" in paste and "能源电力" in paste


def test_index_kind_and_latest() -> None:
    assert build_index.report_kind(Path("A股收盘报告_2026-09-22_1510.html"), "A股收盘报告") == "close"
    assert build_index.report_kind(Path("A股收盘对照_2026-09-21_1510.html"), "对照") == "close"
    assert build_index.report_kind(Path("A股开盘前早报_2026-09-22_0830.html"), "A股开盘前早报") == "open"
    assert build_index.is_indexed_ashare(Path("archive/global/2026/09/全球市场复盘_2026-09-26_2330.html")) is False
    assert build_index.is_indexed_ashare(Path("archive/2026/09/A股开盘前早报_2026-09-24_0830.html")) is True

    reports = sorted(
        (
            build_index.parse_report(p)
            for p in (ROOT / "archive").rglob("*.html")
            if build_index.is_indexed_ashare(p)
        ),
        key=lambda r: r["sort_key"],
        reverse=True,
    )
    assert build_index.report_kind(Path("A股周度复盘_2026-09-24_2000.html"), "A股周度复盘") == "weekly"
    assert build_index.report_kind(Path("美股复盘_2026-09-25.html"), "美股复盘") == "us"
    assert build_index.report_kind(Path("美股周报_2026-09-25.html"), "美股周报") == "us"
    assert build_index.report_kind(Path("全球市场报告_2026-09-25.html"), "全球市场早报") == "global"
    assert build_index.report_kind(Path("美股潜力股与名人持仓雷达_2026-09-27.html"), "持仓雷达") == "radar"
    assert build_index.is_indexed_ashare(Path("archive/global/2026/09/全球市场复盘_2026-09-27_1630.html")) is False
    assert build_index.is_indexed_ashare(Path("archive/2026/09/A股周度复盘_2026-09-24_2000.html")) is True

    reports = build_index.load_archive_reports()
    assert reports
    opens = [r for r in reports if r["kind"] == "open"]
    closes = [r for r in reports if r["kind"] == "close"]
    assert opens, "archive 里应有早报"
    assert closes, "archive 里应有收盘报告"
    html_index = build_index.render_index(reports)
    assert "ashare/" in html_index and "名人持仓雷达" in html_index
    assert "<article" not in html_index
    pages = build_index.render_section_pages(reports)
    assert "latest-close.html" in pages["ashare"]
    assert "收盘报告" in pages["ashare"]
    assert "最新收盘" in pages["ashare"]
    assert "最新早报" in pages["ashare"]
    assert "美股复盘" in pages["us"]
    assert "A股开盘前早报" not in pages["us"]
    latest_open = opens[0]
    latest_close = closes[0]
    page = build_index.render_latest(latest_open, empty="暂无早报", jumping="跳转到最新早报")
    assert latest_open["share_name"] in page
    close_page = build_index.render_latest(latest_close, empty="暂无收盘报告", jumping="跳转到最新收盘报告")
    assert latest_close["share_name"] in close_page
    empty_close = build_index.render_latest(None, empty="暂无收盘报告", jumping="跳转到最新收盘报告")
    assert "暂无收盘报告" in empty_close

    latest_html = (ROOT / "latest.html").read_text(encoding="utf-8")
    latest_close_html = (ROOT / "latest-close.html").read_text(encoding="utf-8")
    latest_weekly_html = (ROOT / "latest-weekly.html").read_text(encoding="utf-8")
    assert "2026-10-09_0830.html" in latest_html
    assert "2026-10-09_1800.html" in latest_close_html
    assert "2026-10-09_2000.html" in latest_weekly_html
    assert "<<<<<<<" not in (ROOT / "index.html").read_text(encoding="utf-8")


def test_merge_eligibility() -> None:
    script = ROOT / "scripts/briefing_pr_eligible.sh"

    def eligible(title: str, *files: str) -> int:
        proc = subprocess.run(
            ["bash", str(script), title, *files],
            env={"REPORT_DATE": "2026-09-22"},
            capture_output=True,
            text=True,
        )
        return proc.returncode

    assert eligible("docs: A股收盘报告 2026-09-22", "archive/2026/09/x.html", "latest-close.html") == 0
    assert eligible("docs: A股开盘前早报 2026-09-22", "archive/2026/09/x.html", "latest.html") == 0
    assert eligible("docs: A股周度复盘 2026-09-22", "archive/2026/10/x.html", "latest-weekly.html", "ashare/index.html") == 0
    assert eligible("docs: A股收盘报告 2026-09-22", "README.md") == 1
    assert eligible("docs: 只改提示词 2026-09-22", "archive/2026/09/x.html") == 1


def main() -> None:
    test_prompt_alignment()
    test_index_kind_and_latest()
    test_merge_eligibility()
    print("ok")


if __name__ == "__main__":
    main()
