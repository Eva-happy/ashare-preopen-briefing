#!/usr/bin/env python3
"""Scan archive/**/*.html and regenerate share pages + index."""

from __future__ import annotations

import html
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
SHARE_DIR = ROOT / "r"
SITE = "https://eva-happy.github.io/ashare-preopen-briefing"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TIME_RE = re.compile(r"_(\d{4})\.html$")


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def is_indexed_ashare(path: Path) -> bool:
    """A-share index only. Global recap HTML lives under archive/global and must not become latest.html."""
    if "global" in path.parts:
        return False
    if "全球市场" in path.name:
        return False
    return True


def report_kind(path: Path, title: str) -> str:
    blob = f"{path.name}\n{title}"
    if "收盘" in blob:
        return "close"
    return "open"


def parse_report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    title_m = TITLE_RE.search(text)
    h1_m = H1_RE.search(text)
    title = strip_tags(title_m.group(1)) if title_m else path.stem
    h1 = strip_tags(h1_m.group(1)) if h1_m else "A股开盘前早报"
    kind = report_kind(path, title)
    date_m = DATE_RE.search(path.name) or DATE_RE.search(title)
    time_m = TIME_RE.search(path.name)
    report_date = date_m.group(1) if date_m else path.stem
    hhmm = time_m.group(1) if time_m else "0000"
    report_time = f"{hhmm[:2]}:{hhmm[2:]}" if time_m else ""
    share_name = f"{report_date}_{hhmm}.html" if time_m else f"{report_date}.html"
    share_rel = f"r/{share_name}"
    archive_rel = path.relative_to(ROOT).as_posix()
    sort_key = f"{report_date}-{hhmm}-{archive_rel}"
    return {
        "path": path,
        "archive_rel": archive_rel,
        "share_rel": share_rel,
        "share_name": share_name,
        "href": share_rel,
        "title": title,
        "h1": h1,
        "kind": kind,
        "date": report_date,
        "time": report_time,
        "sort_key": sort_key,
        "share_url": f"{SITE}/{share_rel}",
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
    }


def sync_share_copies(reports: list[dict]) -> None:
    if SHARE_DIR.exists():
        shutil.rmtree(SHARE_DIR)
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    for r in reports:
        name = r["share_name"]
        if name in used:
            stem = Path(name).stem
            name = f"{stem}_{used.__len__()}.html"
            r["share_name"] = name
            r["share_rel"] = f"r/{name}"
            r["href"] = r["share_rel"]
            r["share_url"] = f"{SITE}/{r['share_rel']}"
        used.add(name)
        target = SHARE_DIR / name
        shutil.copy2(r["path"], target)


KIND_LABEL = {"open": "开盘前早报", "close": "收盘报告"}


def render_index(reports: list[dict]) -> str:
    latest_open = next((r for r in reports if r["kind"] == "open"), None)
    latest_close = next((r for r in reports if r["kind"] == "close"), None)
    cards = []
    for r in reports:
        badges = []
        if latest_open and r["share_rel"] == latest_open["share_rel"]:
            badges.append('<span class="badge">最新早报</span>')
        if latest_close and r["share_rel"] == latest_close["share_rel"]:
            badges.append('<span class="badge badge-close">最新收盘</span>')
        badge = "".join(badges)
        when = (
            f"收盘 {r['time']}"
            if r["kind"] == "close" and r["time"]
            else (f"截止 {r['time']}" if r["time"] else "")
        )
        meta_bits = [x for x in [r["date"], when, f"更新 {r['mtime']}"] if x]
        meta = " ｜ ".join(meta_bits)
        label = KIND_LABEL[r["kind"]]
        cards.append(
            f"""      <article class="card">
        <a class="card-main" href="{html.escape(r['href'])}">
          <div class="card-top">{badge}<span class="label">{html.escape(label)}</span></div>
          <h2>{html.escape(r['h1'])}</h2>
          <p class="meta">{html.escape(meta)}</p>
          <p class="title">{html.escape(r['title'])}</p>
          <span class="cta">打开报告 →</span>
        </a>
        <p class="share-line">分享链接（复制到微信等 App）：<br><code>{html.escape(r['share_url'])}</code></p>
      </article>"""
        )
    cards_html = (
        "\n".join(cards)
        if cards
        else '      <p class="empty">暂无报告。生成后放入 <code>archive/年/月/</code> 再运行 <code>python3 scripts/build_index.py</code>。</p>'
    )
    latest_url = f"{SITE}/latest.html"
    latest_close_url = f"{SITE}/latest-close.html"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="light">
  <meta name="description" content="A股开盘前早报与收盘报告索引。复制 Pages 链接即可在微信等 App 中以网页方式打开。">
  <title>A股早报与收盘报告｜报告索引</title>
  <style>
    :root{{--ink:#172033;--muted:#667085;--line:#e5e9f0;--bg:#f5f7fb;--card:#fff;--blue:#1d4ed8}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
    a{{color:inherit;text-decoration:none}}.wrap{{width:min(880px,100%);margin:auto;padding:18px}}
    .hero{{background:linear-gradient(135deg,#172554,#1e3a8a);color:#fff;padding:28px;border-radius:18px;box-shadow:0 12px 30px #17255422}}
    h1{{font-size:clamp(24px,5vw,36px);line-height:1.15;margin:0 0 10px}}.hero p{{margin:0;opacity:.9}}
    .share-box{{margin:16px 0;padding:14px 16px;background:#fff;border:1px solid var(--line);border-radius:14px}}
    .share-box h2{{margin:0 0 8px;font-size:16px}}.share-box ol{{margin:0;padding-left:1.2em;color:#334155}}.share-box li{{margin:6px 0}}
    .share-box code,.share-line code{{display:inline-block;margin-top:4px;padding:2px 6px;background:#eef2ff;border-radius:6px;font-size:12px;color:#1e3a8a;overflow-wrap:anywhere}}
    .warn{{margin-top:10px;padding:10px 12px;background:#fffbeb;border-left:4px solid #b45309;border-radius:8px;color:#92400e;font-size:13px}}
    .hint{{margin:12px 0 8px;color:var(--muted);font-size:13px}}.hint a{{color:var(--blue);text-decoration:underline}}
    .list{{display:grid;gap:12px;margin-top:8px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
    .card-main{{display:block}}.card-main:hover .cta,.card-main:focus-visible .cta{{text-decoration:underline}}
    .card-top{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}.label{{color:var(--muted);font-size:13px}}
    .badge{{display:inline-block;padding:2px 8px;border-radius:999px;background:#dbeafe;color:#1e40af;font-size:12px;font-weight:700}}.badge-close{{background:#ffedd5;color:#9a3412}}
    h2{{margin:0 0 6px;font-size:20px}}.meta{{margin:0;color:var(--muted);font-size:13px}}.title{{margin:8px 0 12px;color:#334155}}
    .cta{{color:var(--blue);font-weight:700}}.share-line{{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}}
    .empty{{padding:20px;background:#fff;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}}
    footer{{margin:28px 0 8px;padding:16px 18px;background:#172554;color:#fff;border-radius:14px;font-size:13px;opacity:.95}}
    code{{font-size:12px}}
    @media(max-width:430px){{.wrap{{padding:12px}}.hero{{padding:20px}}}}
  </style>
</head>
<body>
<main class="wrap">
  <header class="hero">
    <p>A股开盘前研究 · 收盘报告</p>
    <h1>报告索引</h1>
    <p>网页版早报和收盘报告。复制下方链接，即可分享到微信等 App 直接打开（不是源码）。</p>
  </header>

  <section class="share-box" aria-label="如何分享">
    <h2>如何分享到其他 App</h2>
    <ol>
      <li>不要用 GitHub 文件页的「分享」——那是源码链接，微信里会显示代码。</li>
      <li>复制本站链接：早报 <code>{html.escape(latest_url)}</code>；收盘报告 <code>{html.escape(latest_close_url)}</code></li>
      <li>粘贴到微信 / 备忘录 / 浏览器，对方点开就是排版好的 HTML 报告。</li>
    </ol>
    <div class="warn">仓库需设为 <b>Public</b> 并启用 GitHub Pages，别人才能打开这些链接。</div>
  </section>

  <p class="hint">最新早报：<a href="latest.html">latest.html</a>。最新收盘报告：<a href="latest-close.html">latest-close.html</a>。</p>
  <section class="list" aria-label="报告列表">
{cards_html}
  </section>
  <footer>
    站点地址<br>
    <code>{html.escape(SITE)}/</code>
  </footer>
</main>
</body>
</html>
"""


def render_latest(report: dict | None, *, empty: str, jumping: str) -> str:
    if not report:
        return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>暂无报告</title></head>
<body><p>{html.escape(empty)}</p></body></html>
"""
    href = html.escape(report["href"])
    title = html.escape(report["title"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="refresh" content="0; url={href}">
  <link rel="canonical" href="{href}">
  <title>{html.escape(jumping)}｜{title}</title>
  <script>location.replace({report["href"]!r})</script>
</head>
<body>
  <p>正在打开：<a href="{href}">{title}</a></p>
</body>
</html>
"""


def main() -> None:
    reports = sorted(
        (parse_report(p) for p in ARCHIVE.rglob("*.html") if is_indexed_ashare(p)),
        key=lambda r: r["sort_key"],
        reverse=True,
    )
    sync_share_copies(reports)
    latest_open = next((r for r in reports if r["kind"] == "open"), None)
    latest_close = next((r for r in reports if r["kind"] == "close"), None)
    (ROOT / "index.html").write_text(render_index(reports), encoding="utf-8")
    (ROOT / "latest.html").write_text(
        render_latest(latest_open, empty="暂无早报。请先生成 archive 下的 HTML 早报。", jumping="跳转到最新早报"),
        encoding="utf-8",
    )
    (ROOT / "latest-close.html").write_text(
        render_latest(
            latest_close,
            empty="暂无收盘报告。请先生成 archive 下的 HTML 收盘报告。",
            jumping="跳转到最新收盘报告",
        ),
        encoding="utf-8",
    )
    print(f"indexed {len(reports)} report(s); share copies in r/")
    for r in reports[:5]:
        print(f" - {r['share_url']}")


if __name__ == "__main__":
    main()
