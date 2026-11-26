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
HIGH_RES_LABEL = re.compile(r"\b(?:high[- ]resolution|full[- ]resolution|standalone)\b", re.I)
REVISION = re.compile(r"\b(\d{2}[A-Z]?)\b")


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


def _sections(source):
    """Read headings in their original order; do not equate 'round 2' with latest."""
    heading = None
    lines = []
    for line in source.splitlines():
        if line.startswith("## "):
            if heading is not None:
                yield heading, lines
            heading, lines = line[3:].strip(), []
        elif heading is not None:
            lines.append(line)
    if heading is not None:
        yield heading, lines


def _chart_for_revision(revision):
    if revision is None:
        return None
    number = int(revision[:2])
    return next((n for n, (lo, hi) in ID_RANGES.items() if lo <= number <= hi), None)


def _asset_kind(label, url):
    """Describe the actual linked output, independent of pixel dimensions."""
    s = label.casefold()
    if urlparse(url).netloc == "flow.google.com" or "video" in s or "clip" in s:
        return "video"
    if any(x in s for x in ("comparison", "before/after", " vs ", "close-up", "closeup")):
        return "comparison"
    if any(x in s for x in ("four-frame", "four-phase", "4-phase", "contact sheet", "card", "four-pose")):
        return "contact card"
    if HIGH_RES_LABEL.search(s) or "single frame" in s or "start frame" in s:
        return "standalone still"
    if "diagnostic" in s or "tracking" in s:
        return "diagnostic"
    return "image"


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


def _high_res_stills(folder, index, charts):
    """Link separately rendered full-res stills already named in review notes.

    Do not infer that every four-pose contact card is a high-resolution *single*
    frame. Only explicit still links qualify, and each retains its source record.
    """
    records = [(n, INVENTORIES[n], (folder / INVENTORIES[n]).read_text(encoding="utf-8"))
               for n in charts]
    records.append((None, INDEX, index))
    seen = set()
    stills = []
    for source_chart, source_name, text in records:
        for line in text.splitlines():
            for link in LINK.finditer(line):
                label = _plain(link.group(1))
                url = link.group(2)
                if (_asset_kind(label, url) != "standalone still" or
                        not _image_url(url) or url in seen):
                    continue
                chart_match = re.search(r"\bChart\s+([1-6])\b", line, re.I)
                chart = source_chart or (int(chart_match.group(1)) if chart_match else None)
                if chart not in charts:
                    continue
                seen.add(url)
                # Some labels just say 'full-resolution frame'. Pair those
                # with the exact numbered revision in the surrounding note.
                prefix = _plain(line[:link.start()])
                ids = re.findall(r"\b(\d{2}[A-Z]?)\b", prefix)
                title = label if re.match(r"^\d{2}[A-Z]?\b", label) else (
                    f"{ids[-1]} — {label}" if ids else label)
                state = _state(title)
                if "REVIEW REQUIRED" in title.upper():
                    state = "REVIEW ONLY"
                if "identity HOLD" in line and "29H" in title:
                    state = "HOLD"
                stills.append({"chart": chart, "title": title, "url": url,
                               "summary": _plain(line), "state": state,
                               "kind": "standalone still",
                               "source": source_name})
    return sorted(stills, key=lambda item: item["chart"])


def _current_refinements(index, charts):
    """Prefer current 'Latest test' sections over older round-number headings.

    For a numbered exercise, show only its newest revision. Keep the earlier
    attempts in the linked record, not in the current-output slot.
    """
    sections = list(_sections(index))
    current = [(title, lines) for title, lines in sections
               if title.casefold().startswith("latest test")]
    if not current:
        # Older batches used a 'Most recent round N' heading. Preserve this
        # compatibility path, but don't prefer it when newer sections exist.
        return [{"title": _plain(link.group(1)), "url": link.group(2),
                 "summary": _plain(line), "state": _state(_plain(line)),
                 "kind": _asset_kind(_plain(link.group(1)), link.group(2)),
                 "source": INDEX}
                for heading, lines in sections if heading.casefold().startswith("most recent")
                for line in lines if line.lstrip().startswith("- ")
                for link in [_first_link(line)] if link is not None
                if not charts or any(f"Chart {n}" in line for n in charts)]
    output = []
    seen_exercises = set()
    for heading, lines in current:
        revision = next(iter(REVISION.findall(heading)), None)
        chart = _chart_for_revision(revision)
        family = revision[:2] if revision else None
        if chart not in charts or family in seen_exercises:
            continue
        seen_exercises.add(family)
        linked = [(link, _plain(link.group(1)), line)
                  for line in lines for link in LINK.finditer(line)]
        if not linked:
            continue
        candidate = next(((link, label, line) for link, label, line in linked
                          if revision in label and _asset_kind(label, link.group(2))
                          in ("contact card", "standalone still", "video")), None)
        if candidate is None:
            candidate = next(((link, label, line) for link, label, line in linked
                              if _asset_kind(label, link.group(2)) != "comparison"), linked[0])
        link, label, line = candidate
        comparison = next((l.group(2) for l, name, _ in linked
                           if _asset_kind(name, l.group(2)) == "comparison"), None)
        output.append({"chart": chart, "revision": revision, "title": label,
                       "url": link.group(2), "summary": _plain(line),
                       "state": _state(label), "kind": _asset_kind(label, link.group(2)),
                       "comparison": comparison, "source": INDEX})
    return output


def _review_queue(index, latest, items, charts):
    """Show only live candidate decisions and explicit human-eyes requests.

    This is a read-only inbox. Approval happens in the existing review record,
    never through a decorative button or an assistant-generated PASS.
    """
    queue = []
    seen_urls = set()
    for entry in latest:
        if (entry.get("revision") and entry["state"] not in ("HOLD", "REJECT")
                and "review candidate" in entry["summary"].casefold()):
            instruction = re.search(r"\bcompare\s+([^.;]+)", entry["summary"], re.I)
            queue.append({**entry, "state": "NEEDS EYES",
                          "question": ("Compare " + instruction.group(1) if instruction else
                                       "Does this corrected pose look natural and retain the intended movement?")})
            seen_urls.add(entry["url"])
    for heading, lines in _sections(index):
        if "what needs human eyes" not in heading.casefold():
            continue
        for line in lines:
            if not line.lstrip().startswith("- "):
                continue
            match = REVISION.search(_plain(line[:100]))
            revision = match.group(1) if match else None
            chart = _chart_for_revision(revision)
            if chart not in charts:
                continue
            link = _first_link(line)
            asset = next((x for x in items if x.get("test") == revision), None)
            url = link.group(2) if link else (asset or {}).get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            brief = _plain(line).lstrip("- ").split(":", 1)[0]
            questions = re.findall(r"[^.!?]*\?", _plain(line))
            queue.append({"chart": chart, "revision": revision, "title": brief,
                          "url": url, "summary": _plain(line), "state": "NEEDS EYES",
                          "kind": _asset_kind(_plain(link.group(1)), url) if link else
                                  (asset or {}).get("kind", "video"),
                          "question": questions[0].strip() if questions else
                                      _plain(line).split(":", 1)[-1].strip(),
                          "source": INDEX})
    return queue[:3]


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
                          "state": _state(title), "kind": _asset_kind(title, link.group(2)),
                          "source": INVENTORIES[n]})
    latest = _current_refinements(index, charts)
    review_queue = _review_queue(index, latest, items, charts)
    return {"overviews": [overviews[n] for n in charts], "items": items,
            "latest": latest, "review_queue": review_queue,
            "high_res": _high_res_stills(folder, index, charts),
            "record": PHOTO_DIR / INDEX}


def _esc(value):
    return html.escape(str(value), quote=True)


def _tile(item, kind):
    thumb = _image_url(item["url"])
    image_alt = item.get("title") or "Chart {} overview".format(item.get("chart", ""))
    image = (f'<img loading="lazy" src="{_esc(thumb)}" alt="Preview: {_esc(image_alt)}">'
             if thumb else '<span class="placeholder">Open video or record</span>')
    title = item.get("title") or f'Chart {item["chart"]} overview'
    state = item.get("state", "EXPERIMENTAL")
    css = "hold" if state in ("HOLD", "REJECT") else "test"
    description = item.get("summary", item.get("description", ""))
    open_label = "Open full-resolution still ↗" if kind == "still" else "Open output ↗"
    source_link = (f'<a class="source-link" target="_blank" rel="noopener" '
                   f'href="https://github.com/cwarloe/5BX/blob/main/{PHOTO_DIR}/{_esc(item["source"])}">'
                   'Source / QA notes ↗</a>' if kind in ("still", "review", "refinement") else "")
    question = (f'<p class="question"><strong>Review question:</strong> {_esc(item["question"])}</p>'
                if kind == "review" and item.get("question") else "")
    comparison = (f'<a class="source-link" target="_blank" rel="noopener" '
                  f'href="{_esc(item["comparison"])}">Before/after comparison ↗</a>'
                  if item.get("comparison") else "")
    asset_type = f'<span class="asset-type">{_esc(item["kind"])}</span>' if item.get("kind") else ""
    return f'''<article class="tile {kind}">
      <a class="preview" target="_blank" rel="noopener noreferrer" href="{_esc(item['url'])}">
        {image}<span class="open">{open_label}</span></a>
      <div class="body"><div class="tag {css}">{_esc(state)}</div>{asset_type}<h3>{_esc(title)}</h3>
      {question}<p>{_esc(description)}</p>{comparison} {source_link}</div></article>'''


def render_gallery(data, chart=None):
    title = f"Chart {chart}" if chart else "Charts 1–6"
    overview = "".join(_tile(x, "overview") for x in data["overviews"])
    changes = "".join(_tile(x, "refinement") for x in data["latest"])
    decisions = "".join(_tile(x, "review") for x in data["review_queue"])
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
    review = (f'<section id="human-review" class="group">'
              f'<h2>Only these need human eyes · {len(data["review_queue"])} decisions</h2>'
              f'<p class="hint">Click an output to inspect it. Decisions are recorded in the existing review notes; '
              f'this page does not approve or change assets.</p>'
              f'<div class="grid review-grid">{decisions}</div></section>') if decisions else ""
    stills = "".join(_tile(x, "still") for x in data["high_res"])
    high_res = (f'<section id="high-resolution-stills" class="group">'
                f'<h2>Individual higher-resolution photo stills</h2>'
                f'<p class="hint">Separately rendered frames, linked to their original Drive files. '
                f'These are reference or video-test inputs, not automatically approved movements.</p>'
                f'<div class="grid stills">{stills}</div></section>') if stills else ""
    high_res_jump = ('<p><a href="#high-resolution-stills">Jump to individual higher-resolution stills ↓</a></p>'
                     if stills else "")
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
.asset-type {{display:inline-block;margin-left:7px;color:#536574;font-size:.74rem;text-transform:capitalize}}
.question {{background:#eaf6ff;border-left:4px solid #257da6;border-radius:4px;padding:8px;color:#1c4760!important}}
.review {{border:2px solid #9bbccc}} .review .preview {{height:210px}}
.source-link {{display:inline-block;margin-top:10px;font-size:.8rem}}
footer {{color:#526574;font-size:.82rem;margin:30px 0}}
@media(max-width:600px) {{main {{padding:12px}} header.hero {{padding:18px}} .grid {{gap:11px}}}}
@media print {{body {{background:white}} .tile {{break-inside:avoid}}}}
</style></head><body><main>
<header class="hero"><h1>5BX photographic production traveler</h1>
<p>Output-first review of {_esc(title)}. Tap an image to open the actual Drive product; tap a record link only if you want its prompts, tests or history.</p>
<p class="alert">Experimental images and video. No human-approved exercise forms or verified final workout videos are implied by this gallery. Safety and identity holds remain active.</p>
{high_res_jump}
<p><a href="{_esc(record)}" target="_blank" rel="noopener">Canonical mobile index and current decisions ↗</a></p></header>
{review}
<section class="group"><h2>Chart overviews · open the products</h2>
<div class="grid overview-grid">{overview}</div></section>{latest}
{''.join(sections)}
{high_res}
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
          f"{len(data['items'])} numbered products, {len(data['high_res'])} full-res still links, "
          f"{len(data['latest'])} recent updates, {len(data['review_queue'])} human decisions; "
          "zero form approvals granted")


if __name__ == "__main__":
    main()
