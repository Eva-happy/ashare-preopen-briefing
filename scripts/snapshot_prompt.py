#!/usr/bin/env python3
"""Freeze the current prompt files into prompts/archive/. Never overwrite."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
ARCHIVE = PROMPTS / "archive"
VERSION_FILE = PROMPTS / "VERSION"
CHANGELOG = PROMPTS / "CHANGELOG.md"
CANONICAL = "ashare-preopen-briefing.md"
DASHBOARD = "automation-dashboard-prompt.md"
CLOSE = "ashare-close-briefing.md"
TZ = dt.timezone(dt.timedelta(hours=8))


def today(override: str | None = None) -> str:
    if override:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", override):
            raise SystemExit("date 必须是 YYYY-MM-DD")
        return override
    return dt.datetime.now(TZ).strftime("%Y-%m-%d")


def read_version() -> str:
    if not VERSION_FILE.exists():
        return "0.0.0"
    for line in VERSION_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("date:") and ":" not in line:
            return line
        if line.lower().startswith("version:"):
            return line.split(":", 1)[1].strip()
    return VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0]


def write_version(version: str, date: str, slug: str) -> None:
    VERSION_FILE.write_text(
        "\n".join(
            [
                f"version: {version}",
                f"date: {date}",
                "canonical: prompts/ashare-preopen-briefing.md",
                "dashboard: prompts/automation-dashboard-prompt.md",
                "frozen_original: prompts/archive/v0.2.0_2026-09-21_user-original-1-to-7/",
                f"latest_snapshot: prompts/archive/v{version}_{date}_{slug}/",
                "",
            ]
        ),
        encoding="utf-8",
    )


def stamp_version(path: Path, version: str, date: str) -> None:
    text = path.read_text(encoding="utf-8")
    stamped = re.sub(
        r"提示词版本：\d+\.\d+\.\d+（[^）]*）",
        f"提示词版本：{version}（{date}）",
        text,
    )
    if stamped == text and "提示词版本：" not in text:
        return
    path.write_text(stamped, encoding="utf-8")


def prepend_changelog(version: str, date: str, slug: str, notes: str) -> None:
    heading = f"## {version} — {date}\n\n- 归档：`prompts/archive/v{version}_{date}_{slug}/`\n"
    if notes:
        heading += f"- {notes.strip()}\n"
    heading += "\n"
    old = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else "# 提示词变更记录\n\n"
    if re.search(rf"^## {re.escape(version)}\b", old, flags=re.M):
        return
    marker = "## "
    idx = old.find(marker)
    if idx == -1:
        CHANGELOG.write_text(old.rstrip() + "\n\n" + heading, encoding="utf-8")
    else:
        CHANGELOG.write_text(old[:idx] + heading + old[idx:], encoding="utf-8")


def snapshot(version: str, slug: str, notes: str, date: str | None = None) -> Path:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("version 必须是 x.y.z，例如 0.3.0")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", slug):
        raise SystemExit("slug 只用小写英文、数字和连字符")
    date = today(date)
    dest = ARCHIVE / f"v{version}_{date}_{slug}"
    if dest.exists():
        raise SystemExit(f"拒绝覆盖已有归档：{dest.relative_to(ROOT)}")
    files = (CANONICAL, DASHBOARD, CLOSE)
    for name in files:
        src = PROMPTS / name
        if not src.exists():
            raise SystemExit(f"缺少当前文件：{src}")
    stamp_version(PROMPTS / CANONICAL, version, date)
    stamp_version(PROMPTS / DASHBOARD, version, date)
    dest.mkdir(parents=True, exist_ok=False)
    for name in files:
        shutil.copy2(PROMPTS / name, dest / name)
    manifest = {
        "version": version,
        "date": date,
        "slug": slug,
        "notes": notes,
        "immutable": True,
        "files": list(files),
    }
    (dest / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_version(version, date, slug)
    prepend_changelog(version, date, slug, notes)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="把当前提示词冻结进 prompts/archive/，不会覆盖旧版")
    parser.add_argument("--version", required=True, help="新版本号，例如 0.4.0")
    parser.add_argument("--slug", required=True, help="英文短名，例如 plus-calendar")
    parser.add_argument("--notes", default="", help="写入 CHANGELOG 的一句说明")
    parser.add_argument("--date", default=None, help="归档日期 YYYY-MM-DD，默认北京时间当天")
    args = parser.parse_args()
    dest = snapshot(args.version, args.slug, args.notes, args.date)
    print(f"已归档 {dest.relative_to(ROOT)}")
    print(f"当前版本写入 {VERSION_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
