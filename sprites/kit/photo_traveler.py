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
FLOW_STATIONS = ("Hold / rework", "Still / form QA", "Human review",
                 "Video QC", "Unclassified")


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


def _review_queue(index, latest, items, charts, limit=3):
    """Show existing early-feedback questions, not a mandatory approval queue.

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
    return queue[:limit] if limit is not None else queue


def _revision_rank(item):
    """Prefer an explicit later variant, but not an unrelated diagnostic.

    IDs represent test families, not guaranteed one-to-one physical exercises.
    A repaired 35R can supersede rejected 35 without rewriting that history.
    """
    revision = item.get("test", "")
    letter = revision[2:]
    non_diagnostic = item.get("kind") not in ("diagnostic", "comparison")
    if "diagnostic" in item.get("title", "").casefold():
        non_diagnostic = False
    return (int(non_diagnostic), ord(letter) if letter else 0)


def _current_safety_state(item):
    """A source-level veto overrides optimistic *assistant* grading.

    Read the candidate label first: a source sentence can mention an older
    rejected predecessor or an approved *identity master* without describing
    the current output. This is not a human approval parser.
    """
    title = item.get("title", "")
    direct = _state(title)
    if direct in ("HOLD", "REJECT"):
        return direct
    summary = item.get("summary", "")
    # A same-candidate narrative veto is still binding when the link label is
    # neutral. Historical clauses do not automatically veto later corrections.
    for clause in re.split(r"[.;|]", summary):
        lower = clause.casefold()
        if re.search(r"\b(?:older|earlier|previous|prior|original|historical|superseded)\b", lower):
            continue
        if re.search(r"\b(?:safety|identity|form|human|owner|user|current|still)\b", lower):
            if re.search(r"\b(?:on hold|safety hold|identity hold|hold)\b", lower):
                return "HOLD"
            if re.search(r"\b(?:reject|rejected)\b", lower):
                return "REJECT"
    return None


def _flow_rows(items, latest, review_queue):
    """Read-only Kanban-style projection of existing numbered QA outputs.

    Do not pretend a gallery entry tracks an agent's live assignment or elapsed
    stage duration. Only explicit current outcomes can create review/hold status.
    """
    current = {}
    for item in items:
        family = item["test"][:2]
        if family not in current or _revision_rank(item) > _revision_rank(current[family]):
            current[family] = item
    # The chronological latest-refinement headings supersede inventory cards.
    for item in latest:
        if item.get("revision"):
            current[item["revision"][:2]] = item
    queue = {entry["revision"][:2]: entry for entry in review_queue
             if entry.get("revision")}
    rows = []
    for family, item in sorted(current.items(), key=lambda pair: (pair[1]["chart"], pair[0])):
        revision = item.get("revision") or item.get("test")
        veto = _current_safety_state(item)
        review = queue.get(family)
        kind = item.get("kind", "image")
        if veto:
            station = "Hold / rework"
            state = veto
            blocker = f"Current {state} recorded for this test candidate; see its QA source."
            action = "Resolve the documented defect and recheck form before any video use."
        elif kind == "video":
            station = "Video QC"
            state = "NEEDS EYES" if review else "UNVERIFIED"
            blocker = "A video exists, but complete motion, identity and loop are not verified."
            action = (review.get("question") if review else None) or (
                "Review a full playable cycle, foot/hand identity, and the first-to-last frame seam.")
        elif review:
            station = "Human review"
            state = "NEEDS EYES"
            blocker = ("An optional early-feedback question is recorded; it is not a "
                       "production HOLD or a final-review-ready video.")
            action = ("Continue internal QA and video testing. If feedback is later useful: " +
                      (review.get("question") or "consult the linked QA question."))
        elif kind in ("image", "contact card", "standalone still", "diagnostic"):
            station = "Still / form QA"
            state = "CONDITIONAL" if "conditional" in item.get("title", "").casefold() else "UNVERIFIED"
            blocker = "Still/diagnostic evidence only; next production gate not evidenced here."
            action = "Inspect the linked form/identity QA and record the next gate in that source."
        else:
            station = "Unclassified"
            state = "UNVERIFIED"
            blocker = "The existing review record does not establish a production stage."
            action = "Record the stage and a concrete next action in the existing QA note."
        rows.append({"chart": item["chart"], "work_id": family,
                     "revision": revision, "title": item.get("title", family),
                     "station": station, "state": state, "blocker": blocker,
                     "next_action": action, "url": item["url"],
                     "source": item.get("source", INDEX), "kind": kind})
    return rows


def _wip_control(repo_root):
    """Read cap from the existing standard; no live WIP assignments are stored."""
    standard = Path(repo_root) / "sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md"
    try:
        contents = standard.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"limit": None, "active": None, "source": None}
    match = re.search(r"at most\s+(one|two|three|four|five|\d+)\s+release-validation exercises active",
                      contents, re.I)
    word_numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    limit = (word_numbers.get(match.group(1).lower(), None)
             if match and not match.group(1).isdigit() else
             int(match.group(1)) if match else None)
    return {"limit": limit, "active": None,
            "source": "sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md"}


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
    all_reviews = _review_queue(index, latest, items, charts, limit=None)
    review_queue = all_reviews[:3]
    return {"overviews": [overviews[n] for n in charts], "items": items,
            "latest": latest, "review_queue": review_queue,
            "flow": _flow_rows(items, latest, all_reviews),
            "wip": _wip_control(repo_root),
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


def _flow_board(data):
    """Compact evidence board; assignments and approvals are NOT editable here."""
    rows = data.get("flow", [])
    if not rows:
        return ""
    columns = []
    for station in FLOW_STATIONS:
        present = [row for row in rows if row["station"] == station]
        cards = []
        for row in present:
            output = row["url"]
            thumb = _image_url(output)
            image = (f'<img loading="lazy" src="{_esc(thumb)}" alt="Preview of '
                     f'Chart {row["chart"]} test {_esc(row["work_id"])}">'
                     if thumb else '<span class="placeholder">Open output</span>')
            record = (f"https://github.com/cwarloe/5BX/blob/main/{PHOTO_DIR}/"
                      f"{row['source']}")
            state_class = "blocked" if row["station"] == "Hold / rework" else ""
            cards.append(f'''<article class="flow-card {state_class}">
              <a class="flow-preview" href="{_esc(output)}" target="_blank" rel="noopener noreferrer">
                {image}<span>Open output ↗</span></a>
              <div class="flow-copy"><strong>Chart {row["chart"]} · test family {_esc(row["work_id"])}</strong>
                <span class="flow-status">{_esc(row["state"])}</span>
                <p>Current source: {_esc(row["revision"])}</p>
                <p><b>Gate / status:</b> {_esc(row["blocker"])}</p>
                <p><b>Next:</b> {_esc(row["next_action"])}</p>
                <a href="{_esc(record)}" target="_blank" rel="noopener noreferrer">QA/source record ↗</a>
              </div></article>''')
        displayed_station = ("Early feedback (optional)" if station == "Human review" else station)
        columns.append(f'''<section class="flow-lane" aria-label="{_esc(displayed_station)}">
          <h3>{_esc(displayed_station)} <span>{len(present)}</span></h3>
          {''.join(cards) if cards else '<p class="flow-empty">No indexed item with this evidenced status.</p>'}
          </section>''')
    control = data.get("wip", {})
    limit = control.get("limit")
    cap = (f"Documented release-validation WIP limit: {int(limit)}. "
           if limit is not None else "Documented release-validation WIP limit not found. ")
    # The index documents outputs and QA, not when agents pulled work.
    caution = ("Live assignments, blocked age, and per-stage cycle time are not recorded "
               "in these notes; the displayed counts are indexed work families, NOT active WIP. "
               "Ready/generating states cannot be inferred. Early-feedback requests do not "
               "block agent work; verified ready-for-owner-review videos free production WIP. "
               "No final human form approvals are claimed.")
    return f'''<section id="production-flow" class="group">
      <div class="heading"><h2>Production flow · Kanban-lite evidence view</h2>
        <a href="https://github.com/cwarloe/5BX/blob/main/sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md"
          target="_blank" rel="noopener noreferrer">Production rules ↗</a></div>
      <p class="hint">{_esc(cap + caution)} Coverage: numbered tests in the published mobile inventories;
        new unindexed drafts and concurrent agent activity are not automatically included.</p>
      <div class="flow-board" aria-label="Indexed photographic production status">
        {''.join(columns)}</div></section>'''


def with_metrics(data, repo_root, chart=None):
    """Attach observed measurements to a rendered view without a status ledger.

    Kept separate from gallery_data so collecting measurements can inspect
    indexed items without recursively constructing the gallery.
    """
    try:
        from . import photo_metrics
    except ImportError:  # Direct execution of photo_traveler.py.
        import photo_metrics
    data["metrics"] = photo_metrics.collect_metrics(repo_root, chart)
    return data


def _metric_panel(data):
    """Show measurement *coverage* before attempting numeric comparisons."""
    report = data.get("metrics")
    if not report:
        return ""
    metrics = report["measurements"]
    choices = (
        ("first_pass_yield", "First-pass technical yield", "%"),
        ("repeat_attempt_share", "Measured repeat-attempt share", "%"),
        ("cycle_time_hours", "Mean measured stage time", "h"),
        ("credits_per_approved_video", "Credits per approved video", "credits"),
    )
    cards = []
    for key, title, suffix in choices:
        item = metrics[key]
        raw = item["value"]
        value = ("Not measured" if raw is None else
                 f"{raw * 100:.1f}%" if suffix == "%" else
                 f"{raw:.2f} {suffix}")
        cards.append(f'''<article class="metric-card"><h3>{_esc(title)}</h3>
          <strong>{_esc(value)}</strong><p>Recorded samples: {int(item['sample_size'])}</p>
          <p>{_esc(item['note'])}</p></article>''')
    instrumentation = report["instrumentation"]
    known = report.get("other_known_cost_observations", [])
    cost = (f"One separately documented experimental Flow video used "
            f"{_esc(known[0]['credits'])} credits, not total spend or an approval. "
            if len(known) == 1 else "")
    return f'''<section id="production-measurements" class="group">
      <h2>Production measurements · evidence completeness</h2>
      <p class="hint">{_esc(cost)}{int(instrumentation['annotated_attempts'])} instrumented attempts;
      missing timestamps, attempts and costs stay unknown. These are technical observations,
      never proof of a human-approved 5BX exercise.</p>
      <div class="metric-grid">{''.join(cards)}</div></section>'''


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
              f'<h2>Recorded early-feedback questions · {len(data["review_queue"])} shown</h2>'
              f'<p class="hint">Optional: agents continue internal QA and video work without waiting on these. '
              f'Only a fully checked, playable cycle is READY FOR REVIEW; only Charles can mark it DONE. '
              f'This page does not approve or change assets.</p>'
              f'<div class="grid review-grid">{decisions}</div></section>') if decisions else ""
    flow = _flow_board(data)
    metrics = _metric_panel(data)
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
.flow-board {{display:grid;grid-template-columns:repeat(5,minmax(225px,1fr));gap:12px;
overflow-x:auto;padding-bottom:8px}} .flow-lane {{background:#e7edf1;border-radius:12px;padding:9px;min-width:0}}
.flow-lane h3 {{margin:4px 4px 12px;display:flex;justify-content:space-between;gap:7px}}
.flow-lane h3 span {{background:#cfdee8;color:#264258;padding:2px 7px;border-radius:12px;font-size:.82rem}}
.flow-card {{background:#fff;border:1px solid #d1dfe6;border-radius:10px;overflow:hidden;margin:9px 0}}
.flow-card.blocked {{border:2px solid #ca6a61}} .flow-preview {{display:flex;align-items:center;
justify-content:space-between;gap:6px;font-size:.75rem;padding:7px;background:#edf4f9;min-height:70px}}
.flow-preview img {{width:75px;height:52px;object-fit:contain}} .flow-copy {{padding:9px;font-size:.75rem}}
.flow-copy strong {{display:block;font-size:.86rem;margin:0 0 6px}} .flow-copy p {{margin:7px 0;line-height:1.4}}
.flow-copy a {{display:block;margin:7px 0}} .flow-status {{font-size:.68rem;font-weight:800;
color:#5a3600;background:#fff0ce;padding:3px 5px;border-radius:5px}} .flow-empty {{font-size:.78rem;color:#526574}}
.metric-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px}}
.metric-card {{background:white;border:1px solid #d9e2e8;border-radius:12px;padding:12px}}
.metric-card h3 {{font-size:.83rem;color:#415a6a}} .metric-card strong {{font-size:1.1rem}}
.metric-card p {{color:#526574;font-size:.76rem;line-height:1.4;margin:7px 0}}
footer {{color:#526574;font-size:.82rem;margin:30px 0}}
@media(max-width:600px) {{main {{padding:12px}} header.hero {{padding:18px}} .grid {{gap:11px}}
.flow-board {{grid-template-columns:1fr;overflow-x:visible}}}}
@media print {{body {{background:white}} .tile {{break-inside:avoid}}}}
</style></head><body><main>
<header class="hero"><h1>5BX photographic production traveler</h1>
<p>Output-first review of {_esc(title)}. Tap an image to open the actual Drive product; tap a record link only if you want its prompts, tests or history.</p>
<p class="alert">Experimental images and video. No human-approved exercise forms or verified final workout videos are implied by this gallery. Safety and identity holds remain active.</p>
{high_res_jump}
<p><a href="{_esc(record)}" target="_blank" rel="noopener">Canonical mobile index and current decisions ↗</a></p></header>
{review}
{flow}
{metrics}
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
    data = with_metrics(gallery_data(args.repo_root, args.chart), args.repo_root, args.chart)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_gallery(data, args.chart), encoding="utf-8")
    print(f"Wrote {args.out}: {len(data['overviews'])} chart overviews, "
          f"{len(data['items'])} numbered products, {len(data['high_res'])} full-res still links, "
          f"{len(data['latest'])} recent updates, {len(data['review_queue'])} optional early-feedback questions; "
          "zero form approvals granted")


if __name__ == "__main__":
    main()
