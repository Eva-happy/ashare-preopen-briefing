#!/usr/bin/env python3
"""Local Windows archive for A-share preopen and close HTML reports."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

TZ = dt.timezone(dt.timedelta(hours=8))
DEFAULT_DEST = r"D:\Eva-personal\A股开盘前早报归档"
SITE = "https://eva-happy.github.io/ashare-preopen-briefing"
PAGES_OPEN = f"{SITE}/latest.html"
PAGES_CLOSE = f"{SITE}/latest-close.html"
RAW_SHARE = "https://raw.githubusercontent.com/Eva-happy/ashare-preopen-briefing/main"
KIND_DIR = {"open": "早盘", "close": "收盘"}
KIND_PREFIX = {"open": "A股开盘前早报", "close": "A股收盘报告"}
SKIP_NAMES = {
    "index.html",
    "latest.html",
    "latest-close.html",
    "本地索引.html",
}
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TIME_RE = re.compile(r"_(\d{4})(?:\.html)?$", re.I)
REDIRECT_RE = re.compile(r"r/(\d{4}-\d{2}-\d{2})_(\d{4})\.html", re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)


def today_shanghai() -> dt.date:
    return dt.datetime.now(TZ).date()


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def report_kind(path: Path, title: str = "") -> str | None:
    name = path.name
    if name.lower() in SKIP_NAMES:
        return None
    blob = f"{name}\n{title}"
    if "收盘" in blob:
        return "close"
    if "开盘" in blob or "早报" in blob:
        return "open"
    time_m = TIME_RE.search(path.stem + ".html")
    if time_m:
        hhmm = time_m.group(1)
        if hhmm in {"1510", "1730"}:
            return "close"
        if hhmm == "0830":
            return "open"
    return None


def parse_date_time(path: Path, text: str = "") -> tuple[str, str]:
    date_m = DATE_RE.search(path.name) or DATE_RE.search(text[:800])
    time_m = TIME_RE.search(path.name)
    report_date = date_m.group(1) if date_m else today_shanghai().isoformat()
    hhmm = time_m.group(1) if time_m else ("1510" if "收盘" in path.name else "0830")
    return report_date, hhmm


def target_name(kind: str, report_date: str, hhmm: str) -> str:
    return f"{KIND_PREFIX[kind]}_{report_date}_{hhmm}.html"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def ensure_dirs(root: Path) -> None:
    (root / KIND_DIR["open"]).mkdir(parents=True, exist_ok=True)
    (root / KIND_DIR["close"]).mkdir(parents=True, exist_ok=True)


def iter_html(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.html"):
        if "tools" in path.parts:
            continue
        files.append(path)
    return files


def title_of(path: Path) -> str:
    try:
        match = TITLE_RE.search(read_text(path))
    except OSError:
        return ""
    if not match:
        return ""
    return strip_tags(match.group(1))


def organize(root: Path) -> dict[str, list[Path]]:
    ensure_dirs(root)
    moved: dict[str, list[Path]] = {"open": [], "close": [], "skip": []}
    for path in iter_html(root):
        if path.name.lower() in SKIP_NAMES or path.name == "本地索引.html":
            moved["skip"].append(path)
            continue
        kind = report_kind(path, title_of(path))
        if kind is None:
            moved["skip"].append(path)
            continue
        dest_dir = root / KIND_DIR[kind]
        report_date, hhmm = parse_date_time(path, title_of(path))
        dest = dest_dir / target_name(kind, report_date, hhmm)
        dest_dir.mkdir(parents=True, exist_ok=True)
        if path.resolve() == dest.resolve():
            continue
        shutil.copy2(path, dest)
        if path.parent == root or path.parent == dest_dir:
            try:
                path.unlink()
            except OSError:
                pass
        moved[kind].append(dest)
    write_local_index(root)
    return moved


def write_local_index(root: Path) -> Path:
    ensure_dirs(root)
    cards = []
    for kind in ("open", "close"):
        folder = root / KIND_DIR[kind]
        files = sorted(folder.glob("*.html"), reverse=True)
        if not files:
            cards.append(
                f'<section class="col"><h2>{html.escape(KIND_DIR[kind])}</h2>'
                f'<p class="empty">还没有{html.escape(KIND_DIR[kind])} HTML。</p></section>'
            )
            continue
        items = []
        for path in files:
            rel = path.relative_to(root).as_posix()
            items.append(
                f'<li><a href="{html.escape(rel)}">{html.escape(path.stem)}</a></li>'
            )
        cards.append(
            f'<section class="col"><h2>{html.escape(KIND_DIR[kind])}</h2>'
            f'<ul>{"".join(items)}</ul></section>'
        )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>A股早盘 / 收盘本地归档</title>
  <style>
    body{{margin:0;background:#f5f7fb;color:#172033;font:15px/1.6 -apple-system,"Microsoft YaHei",sans-serif}}
    .wrap{{width:min(880px,100%);margin:auto;padding:20px}}
    h1{{margin:0 0 8px}} .grid{{display:grid;gap:16px;grid-template-columns:1fr 1fr}}
    .col{{background:#fff;border:1px solid #e5e9f0;border-radius:14px;padding:16px}}
    ul{{padding-left:1.2em}} a{{color:#1d4ed8}} .empty{{color:#667085}}
    @media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>
<main class="wrap">
  <h1>A股早盘 / 收盘本地归档</h1>
  <p>双击「生成早盘报告.bat」或「生成收盘报告.bat」会把最新 HTML 存进对应文件夹。</p>
  <div class="grid">
    {"".join(cards)}
  </div>
</main>
</body>
</html>
"""
    out = root / "本地索引.html"
    out.write_text(page, encoding="utf-8")
    return out


def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ashare-local-archive/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def looks_like_report(text: str) -> bool:
    if "<html" not in text.lower():
        return False
    if "暂无收盘" in text or "暂无早报" in text or "暂无报告" in text:
        return False
    return True


def resolve_share(text: str) -> tuple[str, str] | None:
    match = REDIRECT_RE.search(text)
    if not match:
        return None
    return match.group(1), match.group(2)


def fetch_kind(root: Path, kind: str, *, from_repo: Path | None = None) -> Path:
    ensure_dirs(root)
    dest_dir = root / KIND_DIR[kind]
    dest_dir.mkdir(parents=True, exist_ok=True)

    if from_repo is not None:
        html_files = []
        archive = from_repo / "archive"
        if archive.exists():
            for path in archive.rglob("*.html"):
                if report_kind(path) == kind:
                    html_files.append(path)
        if not html_files:
            raise FileNotFoundError(f"仓库 archive 里还没有{KIND_DIR[kind]} HTML")
        src = sorted(html_files, key=lambda p: p.name)[-1]
        text = read_text(src)
        report_date, hhmm = parse_date_time(src, text)
        dest = dest_dir / target_name(kind, report_date, hhmm)
        dest.write_text(text, encoding="utf-8")
        write_local_index(root)
        return dest

    pages = PAGES_CLOSE if kind == "close" else PAGES_OPEN
    try:
        latest_html = http_get(pages)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise FileNotFoundError(
                f"还没有发布{KIND_DIR[kind]}。收盘请等自动任务 17:40 跑完并进入 main。"
            ) from exc
        raise
    resolved = resolve_share(latest_html)
    if not resolved:
        raise FileNotFoundError(
            f"还没有发布{KIND_DIR[kind]}。收盘请等自动任务 17:40 跑完并进入 main。"
        )
    report_date, hhmm = resolved
    share_url = f"{SITE}/r/{report_date}_{hhmm}.html"
    raw_url = f"{RAW_SHARE}/r/{report_date}_{hhmm}.html"
    text = None
    last_error: Exception | None = None
    for url in (share_url, raw_url):
        try:
            candidate = http_get(url)
            if looks_like_report(candidate):
                text = candidate
                break
        except urllib.error.URLError as exc:
            last_error = exc
    if not text:
        raise FileNotFoundError(
            f"下载{KIND_DIR[kind]}失败：{last_error or '页面不是完整报告'}"
        )
    dest = dest_dir / target_name(kind, report_date, hhmm)
    dest.write_text(text, encoding="utf-8")
    write_local_index(root)
    return dest


def copy_repo_reports(repo_root: Path, dest: Path) -> dict[str, int]:
    counts = {"open": 0, "close": 0}
    archive = repo_root / "archive"
    if not archive.exists():
        return counts
    ensure_dirs(dest)
    for path in archive.rglob("*.html"):
        kind = report_kind(path)
        if kind is None:
            continue
        text = read_text(path)
        report_date, hhmm = parse_date_time(path, text)
        target = dest / KIND_DIR[kind] / target_name(kind, report_date, hhmm)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        counts[kind] += 1
    return counts


def kit_and_repo(script_path: Path) -> tuple[Path, Path]:
    kit_root = script_path.resolve().parent
    if kit_root.name == "tools":
        kit_root = kit_root.parent
    repo_root = kit_root.parent
    return kit_root, repo_root


def install(dest: Path, repo_root: Path, kit_root: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    ensure_dirs(dest)
    for name in ("生成早盘报告.bat", "生成收盘报告.bat", "整理归档.bat", "使用说明.txt"):
        src = kit_root / name
        if src.exists():
            shutil.copy2(src, dest / name)
    tools = dest / "tools"
    tools.mkdir(exist_ok=True)
    src_py = kit_root / "tools" / "local_archive.py"
    if src_py.exists():
        shutil.copy2(src_py, tools / "local_archive.py")
    copy_repo_reports(repo_root, dest)
    organize(dest)
    write_local_index(dest)
    return dest


def maybe_open(path: Path, enabled: bool) -> None:
    if not enabled:
        return
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        os.system(f'open "{path}"')
    else:
        os.system(f'xdg-open "{path}" >/dev/null 2>&1 || true')


def print_moved(moved: dict[str, list[Path]]) -> None:
    print(f"早盘 {len(moved['open'])} 份，收盘 {len(moved['close'])} 份")
    for kind in ("open", "close"):
        for path in moved[kind]:
            print(f"  [{KIND_DIR[kind]}] {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="整理并生成本地早盘/收盘 HTML 归档")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_org = sub.add_parser("organize", help="把已有 HTML 分进 早盘/ 收盘/")
    p_org.add_argument("--root", default=DEFAULT_DEST)

    p_fetch = sub.add_parser("fetch", help="下载最新一期 HTML 到对应文件夹")
    p_fetch.add_argument("--kind", choices=("open", "close"), required=True)
    p_fetch.add_argument("--root", default=DEFAULT_DEST)
    p_fetch.add_argument("--from-repo", default=None, help="从本仓库 archive 复制，不访问网络")
    p_fetch.add_argument("--open", action="store_true", dest="open_file")

    p_install = sub.add_parser("install", help="安装到本机归档目录")
    p_install.add_argument("--dest", default=DEFAULT_DEST)
    p_install.add_argument("--repo-root", default=None)

    args = parser.parse_args(argv)
    kit_root, repo_root = kit_and_repo(Path(__file__))

    if args.cmd == "organize":
        moved = organize(Path(args.root))
        print_moved(moved)
        print(f"索引：{Path(args.root) / '本地索引.html'}")
        return 0

    if args.cmd == "fetch":
        from_repo = Path(args.from_repo) if args.from_repo else None
        path = fetch_kind(Path(args.root), args.kind, from_repo=from_repo)
        print(f"已写入 {path}")
        maybe_open(path, args.open_file)
        return 0

    if args.cmd == "install":
        dest = Path(args.dest)
        repo = Path(args.repo_root) if args.repo_root else repo_root
        install(dest, repo, kit_root)
        print(f"已安装到 {dest}")
        print(f"  早盘：{dest / '早盘'}")
        print(f"  收盘：{dest / '收盘'}")
        return 0

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
    except urllib.error.URLError as exc:
        print(f"网络错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
