#!/usr/bin/env python3
"""Read-only, output-first traveler for the current photographic 5BX pilot.

The existing mobile review Markdown is the record of truth. This module does
not select assets, approve form, upload images, or maintain a second ledger.
"""

import argparse
import html
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


PHOTO_DIR = Path("sprites/docs/photo_batches/2026-11-26")
INDEX = "MOBILE_REVIEW_INDEX.md"
INVENTORIES = {
    1: "REVIEW_INVENTORY.md",
    **{n: f"CHART{n}_PILOT_INVENTORY.md" for n in range(2, 7)},
}
ID_RANGES = {1: (15, 20), 2: (21, 25), 3: (26, 29),
             4: (30, 34), 5: (35, 38), 6: (39, 42)}
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
DRIVE = re.compile(r"^/file/d/([A-Za-z0-9_-]+)/view/?$")


def _plain(value):
    return re.sub(r"[*_`]", "", re.sub(LINK, lambda m: m.group(1), value)).strip()


def _lines_in_section(source, title_words):
    active = False
    for line in source.splitlines():
        if line.startswith("## "):
            active = any(word in line.lower() for word in title_words)
            continue
        if active and line.lstrip().startswith("- "):
            yield line.lstrip()[2:]


def _image_url(url):
    parsed = urlparse(url)
    match = DRIVE.fullmatch(parsed.path)
    if parsed.netloc != "drive.google.com" or not match:
        return None
    return f"https://drive.google.com/thumbnail?id={match.group(1)}&sz=w800"


def _first_link(line):
    for link in LINK.finditer(line):
        if urlparse(link.group(2)).scheme == "https":
            return link
    return None


def _number(line, chart):
    # Read the stable test ID from the beginning of a review bullet, not from
    # incidental dates, measurements, or references later in the QA narrative.
    lead = _plain(line[:120])
    match = re.match(r"(?:\[)?\s*(\d{2})([A-Z]?)(?![\w])", lead)
    if not match:
        return None
    number = int(match.group(1))
    lower, upper = ID_RANGES[chart]
    return match.group(0).strip("[] ") if lower <= number <= upper else None


def _state(title):
    upper = title.upper()
    if "HOLD" in upper:
        return "HOLD"
    if "REJECT" in upper:
        return "REJECT"
    return "TEST ONLY"


def gallery_data(repo_root, chart=None):
    """Read current existing notes; fail visibly if a required source is absent."""
    folder = Path(repo_root) / PHOTO_DIR
    index = (folder / INDEX).read_text(encoding="utf-8")
    overviews = {}
    for line in index.splitlines():
        match = re.match(r"^\s*([1-6])\.\s+", line)
        link = _first_link(line) if match else None
        if link:
            n = int(match.group(1))
            overviews[n] = {"chart": n, "url": link.group(2),
                            "description": _plain(line)}
    charts = [chart] if chart else list(INVENTORIES)
    for n in charts:
        if n not in overviews:
            raise ValueError(f"Chart {n} has no overview link in {INDEX}")
    items = []
    for n in charts:
        source = (folder / INVENTORIES[n]).read_text(encoding="utf-8")
        for line in _lines_in_section(source, ("mobile", "review")):
            number = _number(line, n)
            link = _first_link(line)
            if number is None or link is None:
                continue
            label = _plain(link.group(1))
            title = label if label.startswith(number) else f"{number} — {label}"
            items.append({"chart": n, "test": number, "title": title,
                          "url": link.group(2), "summary": _plain(line),
                          "state": _state(title), "source": INVENTORIES[n]})
    # Latest safety/identity vetoes take precedence over the original still
    # inventory; never silently upgrade a candidate based on an older label.
    latest = []
    for line in _lines_in_section(index, ("most recent",)):
        link = _first_link(line)
        if link:
            latest.append({"title": _plain(link.group(1)), "url": link.group(2),
                           "summary": _plain(line), "state": _state(_plain(line))})
    if chart:
        latest = [x for x in latest if f"Chart {chart}" in x["summary"]]
    return {"overviews": [overviews[n] for n in charts], "items": items,
            "latest": latest, "record": PHOTO_DIR / INDEX}


def _esc(value):
    return html.escape(str(value), quote=True)


def _tile(item, kind):
    thumb = _image_url(item["url"])
    image = (f'<img loading="lazy" src="{_esc(thumb)}" alt="Preview: {_esc(item.get("title", f"Chart {item.get("chart", "")}"))}">'
             if thumb else '<span class="placeholder">Open video or record</span>')
    title = item.get("title") or f'Chart {item["chart"]} overview'
    state = item.get("state", "EXPERIMENTAL")
    css = "hold" if state in ("HOLD", "REJECT") else "test"
    description = item.get("summary", item.get("description", ""))
    return f'''<article class="tile {kind}">
      <a class="preview" target="_blank" rel="noopener noreferrer" href="{_esc(item['url'])}">
        {image}<span class="open">Open output ↗</span></a>
      <div class="body"><div class="tag {css}">{_esc(state)}</div><h3>{_esc(title)}</h3>
      <p>{_esc(description)}</p></div></article>'''


def render_gallery(data, chart=None):
    title = f"Chart {chart}" if chart else "Charts 1–6"
    overview = "".join(_tile(x, "overview") for x in data["overviews"])
    changes = "".join(_tile(x, "refinement") for x in data["latest"])
    sections = []
    for top in data["overviews"]:
        n = top["chart"]
        products = [i for i in data["items"] if i["chart"] == n]
        tiles = "".join(_tile(x, "product") for x in products)
        source = f"https://github.com/cwarloe/5BX/blob/main/{PHOTO_DIR}/{INVENTORIES[n]}"
        sections.append(f'''<section id="chart-{n}" class="group">
          <div class="heading"><h2>Chart {n} · Individual outputs</h2>
          <a href="{_esc(source)}" target="_blank" rel="noopener">Read prompts and QA record ↗</a></div>
          <p class="hint">{len(products)} numbered cards and diagnostics · all require human form approval before release.</p>
          <div class="grid products">{tiles}</div></section>''')
    latest = (f'<section class="group"><h2>Latest refinements and safety holds</h2>'
              f'<div class="grid refinements">{changes}</div></section>') if changes else ""
    record = "https://github.com/cwarloe/5BX/blob/main/" + str(data["record"])
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>5BX photographic traveler · {_esc(title)}</title>
<style>
:root {{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#172732;background:#f4f6f8}}
* {{box-sizing:border-box}} body {{margin:0}} main {{max-width:1320px;margin:auto;padding:22px}}
header.hero {{background:#182e3e;color:white;border-radius:18px;padding:25px;margin-bottom:24px}}
h1 {{font-size:clamp(1.6rem,3.3vw,2.6rem);margin:0 0 9px}} h2 {{font-size:1.35rem}}
h3 {{font-size:1rem;margin:7px 0}} a {{color:#135c83}} .hero a {{color:#b8e5ff}}
.hero p {{max-width:920px;line-height:1.5}} .alert {{color:#ffe5a5;font-weight:700}}
.group {{margin:22px 0 35px}} .group h2 {{margin-bottom:7px}} .hint {{color:#526574}}
.heading {{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap}}
.grid {{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,270px),1fr));gap:15px}}
.overview-grid {{grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr))}}
.tile {{background:white;border:1px solid #d9e2e8;border-radius:13px;overflow:hidden;min-width:0}}
.preview {{height:184px;display:flex;position:relative;align-items:center;justify-content:center;background:#dce8ee;overflow:hidden}}
.overview .preview {{height:220px}} .preview img {{width:100%;height:100%;object-fit:contain}}
.placeholder {{font-size:.85rem;color:#436273}} .open {{position:absolute;bottom:9px;right:9px;background:#17374de8;
color:white;border-radius:7px;padding:6px 9px;font-size:.8rem;font-weight:700}}
.body {{padding:12px 14px}} .body p {{font-size:.82rem;line-height:1.42;color:#465764;margin:8px 0 2px;
display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}}
.tag {{display:inline-block;font-size:.68rem;letter-spacing:.04em;font-weight:800;color:#765000;
background:#fff0c7;padding:4px 7px;border-radius:6px}} .tag.hold {{background:#ffe0dd;color:#932e27}}
footer {{color:#526574;font-size:.82rem;margin:30px 0}}
@media(max-width:600px) {{main {{padding:12px}} header.hero {{padding:18px}} .grid {{gap:11px}}}}
@media print {{body {{background:white}} .tile {{break-inside:avoid}}}}
</style></head><body><main>
<header class="hero"><h1>5BX photographic production traveler</h1>
<p>Output-first review of {_esc(title)}. Tap an image to open the actual Drive product; tap a record link only if you want its prompts, tests or history.</p>
<p class="alert">Experimental images and video. No human-approved exercise forms or verified final workout videos are implied by this gallery. Safety and identity holds remain active.</p>
<p><a href="{_esc(record)}" target="_blank" rel="noopener">Canonical mobile index and current decisions ↗</a></p></header>
<section class="group"><h2>Chart overviews · open the products</h2>
<div class="grid overview-grid">{overview}</div></section>{latest}
{''.join(sections)}
<footer>Generated {timestamp} from the existing review inventories. Thumbnails depend on Google Drive viewing permissions;
the “Open output” links work with the viewer's normal Drive access. This page is read-only and does not record approvals.</footer>
</main></body></html>'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--chart", type=int, choices=range(1, 7))
    parser.add_argument("--out", type=Path, default=Path("review-photos.html"))
    args = parser.parse_args(argv)
    data = gallery_data(args.repo_root, args.chart)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_gallery(data, args.chart), encoding="utf-8")
    print(f"Wrote {args.out}: {len(data['overviews'])} chart overviews, "
          f"{len(data['items'])} numbered products, {len(data['latest'])} recent updates; "
          "zero form approvals granted")


if __name__ == "__main__":
    main()
