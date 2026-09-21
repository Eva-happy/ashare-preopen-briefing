#!/usr/bin/env python3
"""Scan archive/**/*.html and regenerate root index.html + latest.html."""

from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TIME_RE = re.compile(r"_(\d{4})\.html$")


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def parse_report(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    title_m = TITLE_RE.search(text)
    h1_m = H1_RE.search(text)
    title = strip_tags(title_m.group(1)) if title_m else path.stem
    h1 = strip_tags(h1_m.group(1)) if h1_m else "A股开盘前早报"
    date_m = DATE_RE.search(path.name) or DATE_RE.search(title)
    time_m = TIME_RE.search(path.name)
    report_date = date_m.group(1) if date_m else ""
    report_time = f"{time_m.group(1)[:2]}:{time_m.group(1)[2:]}" if time_m else ""
    sort_key = f"{report_date}-{time_m.group(1) if time_m else '0000'}-{rel}"
    return {
        "rel": rel,
        "href": quote(rel),
        "title": title,
        "h1": h1,
        "date": report_date,
        "time": report_time,
        "sort_key": sort_key,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
    }


def render_index(reports: list[dict]) -> str:
    cards = []
    for i, r in enumerate(reports):
        badge = '<span class="badge">最新</span>' if i == 0 else ""
        meta_bits = [x for x in [r["date"], r["time"] and f"截止 {r['time']}", f"更新 {r['mtime']}"] if x]
        meta = " ｜ ".join(meta_bits)
        cards.append(
            f"""      <a class="card" href="{html.escape(r['href'])}">
        <div class="card-top">{badge}<span class="label">开盘前早报</span></div>
        <h2>{html.escape(r['h1'])}</h2>
        <p class="meta">{html.escape(meta)}</p>
        <p class="title">{html.escape(r['title'])}</p>
        <span class="cta">打开报告 →</span>
      </a>"""
        )
    cards_html = "\n".join(cards) if cards else '      <p class="empty">暂无报告。生成后放入 <code>archive/年/月/</code> 再运行 <code>python3 scripts/build_index.py</code>。</p>'
    latest_note = (
        f'手机可直接打开 <a href="latest.html">latest.html</a>（当前指向 {html.escape(reports[0]["date"] or reports[0]["title"])}）。'
        if reports
        else "生成报告后会自动更新 latest.html。"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="light">
  <title>A股开盘前早报｜报告索引</title>
  <style>
    :root{{--ink:#172033;--muted:#667085;--line:#e5e9f0;--bg:#f5f7fb;--card:#fff;--blue:#1d4ed8}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
    a{{color:inherit;text-decoration:none}}.wrap{{width:min(880px,100%);margin:auto;padding:18px}}
    .hero{{background:linear-gradient(135deg,#172554,#1e3a8a);color:#fff;padding:28px;border-radius:18px;box-shadow:0 12px 30px #17255422}}
    h1{{font-size:clamp(24px,5vw,36px);line-height:1.15;margin:0 0 10px}}.hero p{{margin:0;opacity:.9}}
    .hint{{margin:16px 0 8px;color:var(--muted);font-size:13px}}.hint a{{color:var(--blue);text-decoration:underline}}
    .list{{display:grid;gap:12px;margin-top:8px}}.card{{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;transition:transform .15s ease,box-shadow .15s ease}}
    .card:hover,.card:focus-visible{{transform:translateY(-1px);box-shadow:0 10px 24px #17255414;outline:none}}
    .card-top{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}.label{{color:var(--muted);font-size:13px}}
    .badge{{display:inline-block;padding:2px 8px;border-radius:999px;background:#dbeafe;color:#1e40af;font-size:12px;font-weight:700}}
    h2{{margin:0 0 6px;font-size:20px}}.meta{{margin:0;color:var(--muted);font-size:13px}}.title{{margin:8px 0 12px;color:#334155}}
    .cta{{color:var(--blue);font-weight:700}}.empty{{padding:20px;background:#fff;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}}
    footer{{margin:28px 0 8px;padding:16px 18px;background:#172554;color:#fff;border-radius:14px;font-size:13px;opacity:.95}}
    code{{font-size:12px}}
    @media(max-width:430px){{.wrap{{padding:12px}}.hero{{padding:20px}}}}
  </style>
</head>
<body>
<main class="wrap">
  <header class="hero">
    <p>A股开盘前研究</p>
    <h1>早报索引</h1>
    <p>点开即可阅读排版后的 HTML 报告（手机浏览器友好）。</p>
  </header>
  <p class="hint">{latest_note}</p>
  <section class="list" aria-label="报告列表">
{cards_html}
  </section>
  <footer>
    启用 GitHub Pages 后，首页一般为<br>
    <code>https://eva-happy.github.io/ashare-preopen-briefing/</code>
  </footer>
</main>
</body>
</html>
"""


def render_latest(report: dict | None) -> str:
    if not report:
        return """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>暂无报告</title></head>
<body><p>暂无报告。请先生成 archive 下的 HTML 早报。</p></body></html>
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
  <title>跳转到最新早报｜{title}</title>
  <script>location.replace({href!r})</script>
</head>
<body>
  <p>正在打开最新报告：<a href="{href}">{title}</a></p>
</body>
</html>
"""


def main() -> None:
    reports = sorted(
        (parse_report(p) for p in ARCHIVE.rglob("*.html")),
        key=lambda r: r["sort_key"],
        reverse=True,
    )
    (ROOT / "index.html").write_text(render_index(reports), encoding="utf-8")
    (ROOT / "latest.html").write_text(render_latest(reports[0] if reports else None), encoding="utf-8")
    print(f"indexed {len(reports)} report(s)")
    for r in reports[:5]:
        print(f" - {r['rel']}")


if __name__ == "__main__":
    main()
