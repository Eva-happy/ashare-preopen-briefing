#!/usr/bin/env python3
"""Scan archive HTML and regenerate the classified Pages portal."""

from __future__ import annotations

import hashlib
import html
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
SHARE_DIR = ROOT / "r"
RADAR_ROOT = ROOT / "us-radar"
SITE = "https://eva-happy.github.io/ashare-preopen-briefing"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TIME_RE = re.compile(r"_(\d{4})\.html$")

# Homepage is only the four entrances. Each market keeps its own page.
SECTIONS: tuple[dict[str, str], ...] = (
    {
        "id": "ashare",
        "slug": "ashare",
        "name": "A股",
        "kicker": "中国市场",
        "blurb": "开盘前早报、收盘报告、周度复盘。",
    },
    {
        "id": "us",
        "slug": "us",
        "name": "美股",
        "kicker": "美国市场",
        "blurb": "美股收盘复盘与周报。",
    },
    {
        "id": "global",
        "slug": "global",
        "name": "全球市场报告",
        "kicker": "跨市场",
        "blurb": "全球主要市场的跨区域报告。",
    },
    {
        "id": "radar",
        "slug": "us-radar",
        "name": "名人持仓雷达",
        "kicker": "披露与持仓",
        "blurb": "名人、政客与机构的持仓和交易披露。",
    },
)
SECTION_BY_ID = {item["id"]: item for item in SECTIONS}
KIND_SECTION = {
    "open": "ashare",
    "close": "ashare",
    "weekly": "ashare",
    "us": "us",
    "global": "global",
    "radar": "radar",
}


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def is_indexed_ashare(path: Path) -> bool:
    """A-share morning, close, and weekly HTML only.

    Global and US files stay out of the A-share list and the latest.html jumps.
    They still appear on their own category pages.
    """
    if "global" in path.parts:
        return False
    name = path.name
    if "全球市场" in name or name.startswith("global-") or "美股" in name:
        return False
    return ("早报" in name) or ("收盘" in name) or ("周度" in name)


def load_archive_reports() -> list[dict]:
    """Index each archive HTML once.

    ``global-*.html`` files are byte-identical ASCII aliases of the Chinese
    ``全球市场复盘`` files. Keep one card and point it at the ASCII path so the
    link does not take an A-share short URL such as ``r/YYYY-MM-DD_0830.html``.
    """
    groups: dict[str, list[Path]] = {}
    for path in ARCHIVE.rglob("*.html"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        groups.setdefault(digest, []).append(path)
    reports: list[dict] = []
    for paths in groups.values():
        aliases = [path for path in paths if path.name.startswith("global-")]
        canonicals = [path for path in paths if not path.name.startswith("global-")]
        if canonicals:
            canonical = sorted(canonicals, key=lambda path: path.as_posix())[0]
            alias = sorted(aliases, key=lambda path: path.as_posix())[0] if aliases else None
        else:
            canonical = sorted(aliases, key=lambda path: path.as_posix())[0]
            alias = None
        item = parse_report(canonical)
        if alias is not None:
            rel = alias.relative_to(ROOT).as_posix()
            item["site_path"] = rel
            item["share_url"] = abs_url(rel)
            item["skip_share"] = True
        reports.append(item)
    reports.sort(key=lambda item: item["sort_key"], reverse=True)
    return reports


def report_kind(path: Path, title: str) -> str:
    blob = f"{path.name}\n{title}"
    if "持仓雷达" in blob or "名人持仓" in blob:
        return "radar"
    if "全球市场" in blob:
        return "global"
    if "美股" in blob:
        return "us"
    if "A股周度" in blob or "周度复盘" in blob:
        return "weekly"
    if "收盘" in blob:
        return "close"
    if "开盘" in blob or "早报" in blob:
        return "open"
    return "other"


def abs_url(site_path: str) -> str:
    quoted = "/".join(quote(part) for part in site_path.split("/"))
    return f"{SITE}/{quoted}"


def href_from_section(slug: str, site_path: str) -> str:
    prefix = f"{slug}/"
    if site_path.startswith(prefix):
        return site_path[len(prefix) :]
    return f"../{site_path}"


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
        "site_path": share_rel,
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
            r["site_path"] = r["share_rel"]
            r["share_url"] = f"{SITE}/{r['share_rel']}"
        used.add(name)
        target = SHARE_DIR / name
        shutil.copy2(r["path"], target)


KIND_LABEL = {
    "open": "开盘前早报",
    "close": "收盘报告",
    "weekly": "周度复盘",
    "us": "美股报告",
    "global": "全球市场",
    "radar": "持仓雷达",
    "other": "其他报告",
}

OTHER_SECTION = {
    "id": "other",
    "slug": "other",
    "name": "其他报告",
    "kicker": "未归类",
    "blurb": "文件名还没有对应到四个分类的报告。",
}

PAGE_CSS = """
    :root{--ink:#172033;--muted:#667085;--line:#e5e9f0;--bg:#f3f6fb;--card:#fff;--blue:#1d4ed8}
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
    a{color:inherit;text-decoration:none}
    .wrap{width:min(960px,100%);margin:auto;padding:18px}
    .hero{background:linear-gradient(135deg,#172554,#1e3a8a);color:#fff;padding:28px;border-radius:18px;box-shadow:0 12px 30px #17255422}
    .hero.ashare{background:linear-gradient(135deg,#172554,#1e3a8a)}
    .hero.us{background:linear-gradient(135deg,#042f2e,#0f766e)}
    .hero.global{background:linear-gradient(135deg,#431407,#c2410c)}
    .hero.radar{background:linear-gradient(135deg,#2e1065,#6d28d9)}
    .hero.other{background:linear-gradient(135deg,#1f2937,#334155)}
    h1{font-size:clamp(26px,5vw,40px);line-height:1.15;margin:0 0 8px}
    .hero p{margin:0;opacity:.92}
    .hero .kicker{margin:0 0 8px;opacity:.85}
    .portal-card{transition:transform .15s ease,border-color .15s ease}
    .kicker{display:block;margin-bottom:6px;font-size:12px;letter-spacing:.08em;font-weight:700;opacity:.8}
    .portal{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}
    .portal-card{display:flex;flex-direction:column;gap:8px;min-height:220px;padding:20px 20px 16px;background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:0 10px 24px #1720330d}
    .portal-card:hover{transform:translateY(-2px);border-color:#cbd5e1}
    .portal-card h2{margin:0;font-size:28px}
    .portal-card .kicker{opacity:1}
    .portal-card.ashare{border-top:5px solid #1d4ed8}.portal-card.ashare .kicker{color:#1d4ed8}
    .portal-card.us{border-top:5px solid #0f766e}.portal-card.us .kicker{color:#0f766e}
    .portal-card.global{border-top:5px solid #c2410c}.portal-card.global .kicker{color:#c2410c}
    .portal-card.radar{border-top:5px solid #6d28d9}.portal-card.radar .kicker{color:#6d28d9}
    .portal-card.other{border-top:5px solid #475569}.portal-card.other .kicker{color:#475569}
    .blurb{margin:0;color:#334155}
    .preview{margin:0;color:var(--muted);font-size:13px}
    .foot{display:flex;justify-content:space-between;align-items:center;margin-top:auto;padding-top:12px}
    .count{color:var(--muted);font-size:13px}
    .share-box{margin:16px 0;padding:14px 16px;background:#fff;border:1px solid var(--line);border-radius:14px}
    .share-box h2{margin:0 0 8px;font-size:16px}
    .share-box p{margin:0;color:#334155}
    .share-box code,.share-line code{display:inline-block;margin-top:4px;padding:2px 6px;background:#eef2ff;border-radius:6px;font-size:12px;color:#1e3a8a;overflow-wrap:anywhere}
    .warn{margin-top:10px;padding:10px 12px;background:#fffbeb;border-left:4px solid #b45309;border-radius:8px;color:#92400e;font-size:13px}
    .switch{display:flex;gap:8px;overflow:auto;margin:14px 0;padding-bottom:2px}
    .switch a{flex:0 0 auto;padding:6px 12px;border-radius:999px;background:#fff;border:1px solid var(--line);color:#334155;font-size:13px;font-weight:700}
    .switch a[aria-current="page"]{background:#172554;border-color:#172554;color:#fff}
    .hint{margin:0 0 8px;color:var(--muted);font-size:13px}
    .hint a{color:var(--blue);text-decoration:underline}
    .list{display:grid;gap:12px;margin-top:8px}
    .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
    .card-main{display:block}
    .card-main:hover .cta,.card-main:focus-visible .cta,.portal-card:hover .cta{text-decoration:underline}
    .card-top{display:flex;align-items:center;gap:8px;margin-bottom:8px}
    .label{color:var(--muted);font-size:13px}
    .badge{display:inline-block;padding:2px 8px;border-radius:999px;background:#dbeafe;color:#1e40af;font-size:12px;font-weight:700}
    .badge-close{background:#ffedd5;color:#9a3412}
    .badge-weekly{background:#ede9fe;color:#5b21b6}
    .badge-us{background:#ccfbf1;color:#115e59}
    .badge-global{background:#ffedd5;color:#9a3412}
    .badge-radar{background:#fae8ff;color:#86198f}
    h2{margin:0 0 6px;font-size:20px}
    .meta{margin:0;color:var(--muted);font-size:13px}
    .title{margin:8px 0 12px;color:#334155}
    .cta{color:var(--blue);font-weight:700}
    .portal-card.ashare .cta{color:#1d4ed8}
    .portal-card.us .cta{color:#0f766e}
    .portal-card.global .cta{color:#c2410c}
    .portal-card.radar .cta{color:#6d28d9}
    .share-line{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
    .empty{padding:20px;background:#fff;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}
    footer{margin:28px 0 8px;padding:16px 18px;background:#172554;color:#fff;border-radius:14px;font-size:13px}
    footer a{color:#fff;text-decoration:underline}
    footer code{color:#fff;font-size:12px}
    code{font-size:12px}
    @media(max-width:720px){.portal{grid-template-columns:1fr}.wrap{padding:12px}.hero{padding:20px}.portal-card{min-height:0}}
"""


def kind_label(report: dict) -> str:
    blob = f"{report.get('title', '')}\n{report.get('archive_rel', '')}"
    if report["kind"] == "us" and ("周报" in blob or "周度" in blob):
        return "美股周报"
    if report["kind"] == "us":
        return "美股复盘"
    return KIND_LABEL.get(report["kind"], "其他报告")


def when_text(report: dict) -> str:
    if report["kind"] == "close" and report["time"]:
        return f"收盘 {report['time']}"
    if report["kind"] == "weekly" and report["time"]:
        return f"周报 {report['time']}"
    if report["time"]:
        return f"截止 {report['time']}"
    return ""


def badge_html(report: dict, peers: list[dict]) -> str:
    first_of_kind: dict[str, dict] = {}
    for item in peers:
        first_of_kind.setdefault(item["kind"], item)
    kind = report["kind"]
    if kind == "open" and first_of_kind.get("open") is report:
        return '<span class="badge">最新早报</span>'
    if kind == "close" and first_of_kind.get("close") is report:
        return '<span class="badge badge-close">最新收盘</span>'
    if kind == "weekly" and first_of_kind.get("weekly") is report:
        return '<span class="badge badge-weekly">最新周报</span>'
    if kind == "us" and "周" in kind_label(report):
        weekly = next((item for item in peers if "周" in kind_label(item)), None)
        if weekly is report:
            return '<span class="badge badge-weekly">最新周报</span>'
    if peers and peers[0] is report and kind == "us":
        return '<span class="badge badge-us">最新</span>'
    if peers and peers[0] is report and kind == "global":
        return '<span class="badge badge-global">最新</span>'
    if peers and peers[0] is report and kind == "radar":
        return '<span class="badge badge-radar">最新</span>'
    if peers and peers[0] is report:
        return '<span class="badge">最新</span>'
    return ""


def render_cards(section: dict, reports: list[dict]) -> str:
    if not reports:
        return '      <p class="empty">这一类还没有报告。</p>'
    cards = []
    for report in reports:
        bits = [report["date"], when_text(report), f"更新 {report['mtime']}"]
        meta = " ｜ ".join(bit for bit in bits if bit)
        href = href_from_section(section["slug"], report["site_path"])
        cards.append(
            f"""      <article class="card">
        <a class="card-main" href="{html.escape(href)}">
          <div class="card-top">{badge_html(report, reports)}<span class="label">{html.escape(kind_label(report))}</span></div>
          <h2>{html.escape(report['h1'])}</h2>
          <p class="meta">{html.escape(meta)}</p>
          <p class="title">{html.escape(report['title'])}</p>
          <span class="cta">打开报告 →</span>
        </a>
        <p class="share-line">分享链接（复制到微信等 App）：<br><code>{html.escape(report['share_url'])}</code></p>
      </article>"""
        )
    return "\n".join(cards)


def stable_links(section_id: str) -> str:
    if section_id == "ashare":
        return (
            '<p class="hint">固定入口：<a href="../latest.html">最新早报</a>'
            ' · <a href="../latest-close.html">最新收盘</a>'
            ' · <a href="../latest-weekly.html">最新周报</a></p>'
        )
    if section_id == "us":
        return '<p class="hint">固定入口：<a href="../latest-us.html">最新美股报告</a></p>'
    if section_id == "radar":
        return '<p class="hint">固定入口：<a href="latest.html">最新雷达</a></p>'
    return ""


def visible_sections(grouped: dict[str, list[dict]]) -> list[dict]:
    items = list(SECTIONS)
    if grouped.get("other"):
        items.append(OTHER_SECTION)
    return items


def render_switch(current: str, grouped: dict[str, list[dict]]) -> str:
    links = ['<a href="../index.html">首页</a>']
    for section in visible_sections(grouped):
        current_attr = ' aria-current="page"' if section["id"] == current else ""
        links.append(
            f'<a href="../{html.escape(section["slug"])}/"{current_attr}>{html.escape(section["name"])}</a>'
        )
    return f'<nav class="switch" aria-label="报告分类">{"".join(links)}</nav>'


def document(*, title: str, description: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="light">
  <meta name="description" content="{html.escape(description)}">
  <title>{html.escape(title)}</title>
  <style>
{PAGE_CSS}
  </style>
</head>
<body>
<main class="wrap">
{body}
</main>
</body>
</html>
"""


def portal_card(section: dict, reports: list[dict]) -> str:
    if reports:
        preview = f"最新：{reports[0]['title']}"
    else:
        preview = "暂无报告"
    count = f"共 {len(reports)} 份"
    return f"""    <a class="portal-card {html.escape(section['id'])}" href="{html.escape(section['slug'])}/">
      <span class="kicker">{html.escape(section['kicker'])}</span>
      <h2>{html.escape(section['name'])}</h2>
      <p class="blurb">{html.escape(section['blurb'])}</p>
      <p class="preview">{html.escape(preview)}</p>
      <span class="foot"><span class="count">{html.escape(count)}</span><span class="cta">进入 →</span></span>
    </a>"""


def render_hub(grouped: dict[str, list[dict]]) -> str:
    cards = "\n".join(portal_card(section, grouped.get(section["id"], [])) for section in visible_sections(grouped))
    body = f"""  <header class="hero">
    <p class="kicker">市场研究报告</p>
    <h1>按市场进入</h1>
    <p>A股、美股、全球市场报告、名人持仓雷达分开展示。先选一类，再打开具体一期。</p>
  </header>
  <nav class="portal" aria-label="报告分类">
{cards}
  </nav>
  <section class="share-box" aria-label="如何分享">
    <h2>如何分享</h2>
    <p>进入对应分类，复制那一期卡片里的 Pages 链接，粘贴到微信、备忘录或浏览器。对方打开的是排版好的网页。</p>
    <div class="warn">不要分享 GitHub 文件页。那是源码链接，微信里会显示代码。仓库需为 <b>Public</b> 并启用 GitHub Pages。</div>
  </section>
  <footer>
    站点地址<br>
    <code>{html.escape(SITE)}/</code>
  </footer>"""
    return document(
        title="市场研究报告｜分类入口",
        description="A股、美股、全球市场报告、名人持仓雷达分开展示。复制 Pages 链接即可在微信等 App 中打开。",
        body=body,
    )


def render_section(section: dict, grouped: dict[str, list[dict]]) -> str:
    reports = grouped.get(section["id"], [])
    body = f"""  <header class="hero {html.escape(section['id'])}">
    <p class="kicker">{html.escape(section['kicker'])}</p>
    <h1>{html.escape(section['name'])}</h1>
    <p>{html.escape(section['blurb'])}</p>
  </header>
  {render_switch(section['id'], grouped)}
  {stable_links(section['id'])}
  <section class="list" aria-label="{html.escape(section['name'])}报告列表">
{render_cards(section, reports)}
  </section>
  <footer>
    <a href="../index.html">返回分类首页</a><br>
    <code>{html.escape(SITE)}/{html.escape(section['slug'])}/</code>
  </footer>"""
    return document(
        title=f"{section['name']}｜市场研究报告",
        description=section["blurb"],
        body=body,
    )


def group_reports(reports: list[dict], radar: list[dict] | None = None) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {item["id"]: [] for item in SECTIONS}
    grouped["other"] = []
    for report in reports:
        if "site_path" not in report:
            report["site_path"] = report["share_rel"]
        grouped[KIND_SECTION.get(report["kind"], "other")].append(report)
    for report in radar or []:
        if "site_path" not in report:
            report["site_path"] = report["share_rel"]
        grouped["radar"].append(report)
    for items in grouped.values():
        items.sort(key=lambda item: item["sort_key"], reverse=True)
    return grouped


def render_index(reports: list[dict], radar: list[dict] | None = None) -> str:
    return render_hub(group_reports(reports, radar))


def render_section_pages(reports: list[dict], radar: list[dict] | None = None) -> dict[str, str]:
    grouped = group_reports(reports, radar)
    pages = {section["id"]: render_section(section, grouped) for section in SECTIONS}
    if grouped["other"]:
        pages["other"] = render_section(OTHER_SECTION, grouped)
    return pages


def load_radar_reports() -> list[dict]:
    archive = RADAR_ROOT / "archive"
    if not archive.exists():
        return []
    found = [parse_report(path) for path in archive.rglob("*.html")]
    for item in found:
        item["kind"] = "radar"
        rel = item["path"].relative_to(RADAR_ROOT).as_posix()
        item["site_path"] = f"us-radar/{rel}"
        item["share_url"] = abs_url(item["site_path"])
    found.sort(key=lambda item: item["sort_key"], reverse=True)
    if found and (RADAR_ROOT / "latest.html").is_file():
        found[0]["site_path"] = "us-radar/latest.html"
        found[0]["share_url"] = f"{SITE}/us-radar/latest.html"
    return found


def write_section_pages(grouped: dict[str, list[dict]]) -> None:
    pages = {section["id"]: render_section(section, grouped) for section in SECTIONS}
    for section in SECTIONS:
        directory = ROOT / section["slug"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(pages[section["id"]], encoding="utf-8")
    other_dir = ROOT / "other"
    if grouped["other"]:
        other_dir.mkdir(parents=True, exist_ok=True)
        (other_dir / "index.html").write_text(render_section(OTHER_SECTION, grouped), encoding="utf-8")
    elif other_dir.exists():
        shutil.rmtree(other_dir)


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
    reports = load_archive_reports()
    sync_share_copies([item for item in reports if not item.get("skip_share")])
    radar = load_radar_reports()
    grouped = group_reports(reports, radar)
    latest_open = next((r for r in reports if r["kind"] == "open" and is_indexed_ashare(r["path"])), None)
    latest_close = next((r for r in reports if r["kind"] == "close" and is_indexed_ashare(r["path"])), None)
    latest_weekly = next((r for r in reports if r["kind"] == "weekly" and is_indexed_ashare(r["path"])), None)
    latest_us = next((r for r in grouped["us"] if r["kind"] == "us"), None)
    (ROOT / "index.html").write_text(render_hub(grouped), encoding="utf-8")
    write_section_pages(grouped)
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
    (ROOT / "latest-weekly.html").write_text(
        render_latest(
            latest_weekly,
            empty="暂无周度复盘。请先生成 archive 下的 HTML 周报。",
            jumping="跳转到最新周度复盘",
        ),
        encoding="utf-8",
    )
    (ROOT / "latest-us.html").write_text(
        render_latest(
            latest_us,
            empty="暂无美股报告。请先生成 archive 下的 HTML 美股报告。",
            jumping="跳转到最新美股报告",
        ),
        encoding="utf-8",
    )
    print(f"indexed {len(reports)} archive report(s), {len(radar)} radar report(s)")
    for section in visible_sections(grouped):
        print(f" - {section['name']}: {len(grouped[section['id']])}")


if __name__ == "__main__":
    main()
