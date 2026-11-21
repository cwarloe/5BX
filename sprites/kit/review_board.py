#!/usr/bin/env python3
"""Generate a self-contained, read-only 5BX artwork review grid.

From the repository root:
  python3 sprites/kit/review_board.py --chart 2 --out review-chart2.html
  python3 sprites/kit/review_board.py --chart 2 --art-root /path/to/restored/sprites --out review-chart2.html

Selections come only from config/strips.json + library/index.json. This does
not approve art, change selection, generate media, or contact an AI service.
"""

import argparse
import base64
import hashlib
import html
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import line, qc_sheet


SLOT_TITLES = {"ex1": "Exercise 1", "ex2": "Exercise 2", "ex3": "Exercise 3",
               "ex4": "Exercise 4", "run": "Exercise 5 · running", "jump": "Exercise 5 · jumping"}


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def review_items(repo_root, chart, art_root=None):
    """Derive six slots, source hashes, technical inspection and approval gaps."""
    sprites = Path(repo_root) / "sprites"
    art = Path(art_root) if art_root is not None else sprites
    registry = _read(sprites / "config/strips.json")
    library = _read(sprites / "library/index.json")
    archive = _read(sprites / "config/art-archive-index.json")
    character = _read(sprites / "config/character.json")
    plan = _read(Path(repo_root) / "data/5bx-charts.json")
    chart_plan = next((c for c in plan["charts"] if c["id"] == chart), None)
    if chart_plan is None:
        raise ValueError(f"Chart {chart} not present in the 5BX exercise plan")
    mapping = registry["charts"].get(str(chart), {})
    direct = {e["path"]: e["drive_id"] for e in archive.get("direct_files", [])}
    descriptions = {str(e["n"]): e for e in chart_plan["exercises"]}
    result = []
    for slot in line.SLOTS:
        strip_id = mapping.get(slot)
        strip = registry["strips"].get(strip_id, {}) if strip_id else {}
        source_rel = "sheets/" + strip["file"] if strip.get("file") else None
        source_path = art / source_rel if source_rel else None
        selected = [e for e in library["entries"] if e.get("strip") == strip_id
                    and e.get("verdict") == "chosen"]
        chosen = selected[0] if len(selected) == 1 else None
        expected_hash = (chosen or {}).get("measured", {}).get("sha")
        actual_hash = (hashlib.sha1(source_path.read_bytes()).hexdigest()[:len(expected_hash)]
                       if source_path and source_path.is_file() and expected_hash else None)
        hash_state = ("MATCH" if actual_hash == expected_hash else "MISMATCH") if actual_hash else "NOT_RUN"
        form_grade = (chosen or {}).get("grades", {}).get("form")
        human_review = bool(chosen and line.reviewed_by_human(chosen) and
                            type(form_grade) is int and form_grade >= 4)
        technical = (qc_sheet.inspect_sheet(source_path, strip["poses"],
                     rows=strip.get("rows", 1), row=strip.get("row", 0),
                     qc=strip.get("qc"), palette=character.get("palette"))
                     if source_path and strip.get("poses") else
                     {"status": "NOT_RUN", "checks": [{"name": "availability", "status": "NOT_RUN",
                      "detail": "Exercise not mapped"}]})
        ref_num = slot[2:] if slot.startswith("ex") else "5"
        reference = sprites / f"prompts/refs/BOOKLET-c{chart}e{ref_num}.png"
        instruction = descriptions.get(ref_num, {})
        blockers = []
        if not strip_id:
            blockers.append("Exercise not mapped")
        if len(selected) != 1:
            blockers.append(f"Expected one chosen image; found {len(selected)}")
        if not human_review:
            blockers.append("Human form approval pending")
        if hash_state != "MATCH":
            blockers.append("Source hash not verified" if hash_state == "NOT_RUN" else "Source differs from chosen version")
        if technical["status"] == "FAIL":
            blockers.append("Technical QC flagged a defect for inspection")
        result.append({"slot": slot, "slot_title": SLOT_TITLES[slot], "strip_id": strip_id,
                       "source_rel": source_rel, "source_path": source_path,
                       "drive_id": direct.get(source_rel), "selected": chosen,
                       "selected_drive_id": direct.get((chosen or {}).get("file")),
                       "selection_count": len(selected), "hash_state": hash_state,
                       "human_review": human_review, "technical": technical,
                       "reference": reference if reference.is_file() else None,
                       "exercise": instruction.get("name", (chosen or {}).get("exercise", "")),
                       "start": instruction.get("start", ""), "movement": instruction.get("movement", ""),
                       "blockers": blockers})
    return result


def _e(value):
    return html.escape(str(value or ""), quote=True)


def _img_uri(path):
    if not path or not Path(path).is_file():
        return None
    try:
        from PIL import Image
        with Image.open(path) as im:
            rgb = im.convert("RGBA")
            rgb.thumbnail((840, 460))
            canvas = Image.new("RGB", rgb.size, "white")
            canvas.paste(rgb, mask=rgb.getchannel("A"))
            stream = io.BytesIO()
            canvas.save(stream, "JPEG", quality=78, optimize=True)
            return "data:image/jpeg;base64," + base64.b64encode(stream.getvalue()).decode("ascii")
    except ImportError:
        return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


def _image(path, alt, empty):
    uri = _img_uri(path)
    return (f'<img alt="{_e(alt)}" src="{uri}" loading="lazy">' if uri else
            f'<div class="empty">{_e(empty)}</div>')


def _chip(label, status):
    css = status.lower().replace("_", "-")
    return f'<span class="chip {css}">{_e(label)}</span>'


def render_html(chart, items, level_order):
    selected_count = sum(i["selected"] is not None for i in items)
    approved = sum(i["human_review"] for i in items)
    inspected = sum(i["technical"]["status"] != "NOT_RUN" for i in items)
    cards = []
    for item in items:
        selected = item["selected"] or {}
        asset_id = selected.get("id", "No chosen asset")
        link = (f'https://drive.google.com/file/d/{_e(item["drive_id"])}/view'
                if item["drive_id"] else "")
        chosen_link = (f'https://drive.google.com/file/d/{_e(item["selected_drive_id"])}/view'
                       if item["selected_drive_id"] else "")
        qc = item["technical"]
        qc_rows = "".join(f'<li>{_chip(x["status"], x["status"])} <strong>{_e(x["name"])}</strong>: '
                          f'{_e(x["detail"])}</li>' for x in qc["checks"])
        blockers = ("".join(f'<li>{_e(b)}</li>' for b in item["blockers"]) or
                    '<li class="good">No artwork release blockers recorded</li>')
        links = (f'<a href="{link}" target="_blank" rel="noopener">Open render sheet in Drive</a>'
                 if link else '<span>Render sheet not indexed in Drive</span>')
        if chosen_link and chosen_link != link:
            links += f' · <a href="{chosen_link}" target="_blank" rel="noopener">Chosen library source</a>'
        note = ' · '.join(filter(None, [item["strip_id"], item["source_rel"]]))
        cards.append(f'''
        <section class="card" id="{_e(item['slot'])}">
          <header><div><small>{_e(item['slot_title'])}</small><h2>{_e(item['exercise'])}</h2>
          <p class="muted">{_e(note)}</p></div><div class="chips">
          {_chip('Chosen' if item['selected'] else 'No selection', 'PASS' if item['selected'] else 'FAIL')}
          {_chip('Form approved' if item['human_review'] else 'Form review pending', 'PASS' if item['human_review'] else 'WARN')}
          {_chip('QC ' + qc['status'], qc['status'])}</div></header>
          <div class="images"><figure><figcaption>Original 5BX booklet reference</figcaption>
          {_image(item['reference'], '5BX booklet illustration', 'Booklet image not available')}</figure>
          <figure class="sheet"><figcaption>Selected render sheet</figcaption>
          {_image(item['source_path'], 'Exercise pose sheet', 'Not restored locally; use the Drive link below')}</figure></div>
          <p class="links">{links}</p>
          <div class="meta"><span>Library ID: <strong>{_e(asset_id)}</strong></span>
          <span>Version hash: {_chip(item['hash_state'], 'PASS' if item['hash_state']=='MATCH' else 'WARN')}</span>
          <span>Technical inspection: {_chip(qc['status'], qc['status'])}</span></div>
          <p><strong>Booklet movement:</strong> {_e(item['movement'])}</p>
          <div class="status"><strong>Release readiness</strong><ul>{blockers}</ul></div>
          <details><summary>Technical inspection details ({len(qc['checks'])})</summary><ul class="checks">{qc_rows}</ul></details>
        </section>''')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>5BX Chart {chart} · Artwork Review Traveler</title>
<style>
:root {{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#27323b;background:#f4f5f5}}
* {{box-sizing:border-box}} body {{margin:0}} main {{max-width:1460px;margin:auto;padding:25px}}
h1 {{margin:.1em 0 .2em;font-size:clamp(1.6rem,3vw,2.5rem)}} h2 {{margin:4px 0;font-size:1.15rem}}
p {{line-height:1.4}} small,.muted {{color:#65727b}} small {{text-transform:uppercase;letter-spacing:.08em}}
.summary {{background:#26323b;color:white;padding:24px;border-radius:16px;margin-bottom:18px}}
.summary p {{margin:.5em 0}} .metrics {{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}}
.metrics div {{min-width:115px;background:#3b4952;padding:10px 15px;border-radius:9px}}
.metrics strong {{font-size:1.4rem;display:block}} .metrics span {{font-size:.78rem;color:#e2e9ec}}
.grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:18px}}
.card {{background:white;border:1px solid #d7dfe1;border-radius:14px;padding:18px;overflow:hidden}}
.card header {{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;border-bottom:1px solid #e8ebee;padding-bottom:10px}}
.card header p {{margin:4px 0;overflow-wrap:anywhere;font-size:.8rem}}
.chips {{display:flex;align-content:start;flex-wrap:wrap;gap:5px}}
.chip {{display:inline-block;border-radius:8px;padding:3px 7px;font-size:.72rem;font-weight:700;background:#dbe3e8;color:#364a57}}
.chip.pass {{background:#d8f4e4;color:#18633e}} .chip.warn,.chip.not-run {{background:#fff0cb;color:#855214}}
.chip.fail,.chip.mismatch {{background:#fbe0dc;color:#9a261a}}
.images {{display:grid;grid-template-columns:minmax(120px,1fr) minmax(190px,2.1fr);gap:10px;margin-top:12px}}
figure {{margin:0;background:#f6f8f9;border:1px solid #e7ebee;border-radius:8px;padding:6px}}
figure img {{width:100%;height:220px;object-fit:contain;display:block}}
figcaption {{font-size:.76rem;font-weight:600;color:#536675;text-align:center;margin:4px}}
.empty {{display:grid;place-items:center;text-align:center;min-height:220px;padding:15px;color:#74818a;font-size:.83rem}}
.links {{font-size:.86rem}} a {{color:#0a5b9a;text-decoration:underline}} a:hover {{color:#e67323}}
.meta {{display:flex;flex-wrap:wrap;gap:10px 20px;font-size:.83rem;color:#44535c}}
.status {{background:#fff8ed;padding:10px 12px;border-left:4px solid #e58a35;border-radius:5px}}
.status ul {{margin:6px 0;padding-left:20px}} li {{margin:3px 0}} .good {{color:#19683e}}
details {{margin-top:12px;border-top:1px solid #e1e6e8;padding-top:9px}}
summary {{cursor:pointer;font-weight:600;font-size:.9rem}} .checks {{font-size:.81rem;list-style:none;padding:0}}
.checks li {{padding:5px 0;border-bottom:1px solid #f0f2f3}}
@media(max-width:530px) {{main {{padding:12px}} .card {{padding:12px}} .images {{grid-template-columns:1fr}}
figure img {{height:185px}} .summary {{padding:17px}}}}
@media print {{body {{background:white}} .card {{break-inside:avoid}} details {{display:none}}}}
</style></head><body><main>
<div class="summary"><small style="color:#ffbd72">5BX · Production review</small>
<h1>Chart {chart}: Artwork Review Traveler</h1>
<p>One read-only view of the existing registry, library selections, original booklet art and technical checks.
No review decision is made or changed here.</p>
<p><strong>All levels use these same chart images:</strong> {_e(', '.join(level_order))}.
Level changes affect exercise counts and timing, not the image selection.</p>
<div class="metrics"><div><strong>6</strong><span>Exercise slots</span></div>
<div><strong>{selected_count}</strong><span>Chosen</span></div>
<div><strong>{approved}</strong><span>Human form approvals</span></div>
<div><strong>{inspected}</strong><span>Technical inspections run</span></div></div></div>
<div class="grid">{''.join(cards)}</div>
<p class="muted">Technical checks screen objective image properties only. A PASS is not proof of correct anatomy or
safe instruction. Approval must be recorded through the existing sprite library grading workflow.
Missing local images are marked NOT_RUN, never treated as a pass.</p>
</main></body></html>'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chart", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--art-root", type=Path, help="Root of restored sprites/ data (sheets/ etc.)")
    parser.add_argument("--out", type=Path, help="Generated HTML file; default: review-chartN.html")
    args = parser.parse_args(argv)
    items = review_items(args.repo_root, args.chart, args.art_root)
    plan = _read(args.repo_root / "data/5bx-charts.json")
    out = args.out or Path(f"review-chart{args.chart}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(args.chart, items, plan["levelOrder"]), encoding="utf-8")
    print(f"Wrote {out}: {sum(i['selected'] is not None for i in items)}/6 selections, "
          f"{sum(i['human_review'] for i in items)}/6 human form approvals, "
          f"{sum(i['technical']['status'] != 'NOT_RUN' for i in items)}/6 technical checks run")


if __name__ == "__main__":
    main()
