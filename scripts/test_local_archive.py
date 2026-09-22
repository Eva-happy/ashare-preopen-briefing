#!/usr/bin/env python3
"""Tests for the local 早盘/收盘 archive helper."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "local-archive" / "tools"))

import local_archive as la  # noqa: E402


def write(path: Path, title: str, body: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<title>{title}</title></head><body><h1>{title}</h1><p>{body}</p></body></html>",
        encoding="utf-8",
    )


def test_organize_and_index(tmp: Path) -> None:
    write(tmp / "A股开盘前早报_2026-09-21_0830.html", "A股开盘前早报｜2026-09-21 08:30")
    write(tmp / "散落收盘.html", "A股收盘报告｜2026-09-21 15:10")
    write(tmp / "2026-09-22_0830.html", "A股开盘前早报｜2026-09-22 08:30")
    write(tmp / "latest.html", "跳转到最新早报")
    moved = la.organize(tmp)
    assert (tmp / "早盘" / "A股开盘前早报_2026-09-21_0830.html").exists()
    assert (tmp / "早盘" / "A股开盘前早报_2026-09-22_0830.html").exists()
    assert (tmp / "收盘" / "A股收盘报告_2026-09-21_1510.html").exists()
    assert not (tmp / "A股开盘前早报_2026-09-21_0830.html").exists()
    assert (tmp / "latest.html").exists()
    assert (tmp / "本地索引.html").exists()
    index = (tmp / "本地索引.html").read_text(encoding="utf-8")
    assert "早盘" in index and "收盘" in index
    assert any(p.name.endswith("0830.html") for p in moved["open"])
    assert any("收盘报告" in p.name for p in moved["close"])


def test_fetch_from_repo(tmp: Path) -> None:
    dest = tmp / "out"
    path = la.fetch_kind(dest, "open", from_repo=ROOT)
    assert path.parent.name == "早盘"
    assert path.name.startswith("A股开盘前早报_")
    text = path.read_text(encoding="utf-8")
    assert "A股开盘前早报" in text
    try:
        la.fetch_kind(dest, "close", from_repo=ROOT)
        raise AssertionError("expected missing close report")
    except FileNotFoundError as exc:
        assert "收盘" in str(exc)


def test_install(tmp: Path) -> None:
    dest = tmp / "D-Eva" / "A股开盘前早报归档"
    kit = ROOT / "local-archive"
    la.install(dest, ROOT, kit)
    assert (dest / "生成收盘报告.bat").exists()
    assert (dest / "生成早盘报告.bat").exists()
    assert (dest / "整理归档.bat").exists()
    assert (dest / "tools" / "local_archive.py").exists()
    opens = list((dest / "早盘").glob("*.html"))
    assert len(opens) >= 2
    assert (dest / "本地索引.html").exists()
    assert "A股开盘前早报" in opens[0].read_text(encoding="utf-8")


def test_kind_helpers() -> None:
    assert la.report_kind(Path("A股收盘报告_2026-09-22_1510.html")) == "close"
    assert la.report_kind(Path("A股开盘前早报_2026-09-22_0830.html")) == "open"
    assert la.report_kind(Path("2026-09-22_1510.html")) == "close"
    assert la.report_kind(Path("latest-close.html")) is None


def main() -> None:
    import tempfile

    test_kind_helpers()
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        test_organize_and_index(tmp / "organize")
        test_fetch_from_repo(tmp / "fetch")
        test_install(tmp / "install")
    print("ok")


if __name__ == "__main__":
    main()
