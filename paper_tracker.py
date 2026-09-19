"""paper_tracker.py -- the standing new-paper sweep for the QEM /
readout / calibration / compiler lanes.

Fetches the arxiv quant-ph new-listing (the export API is
unreachable from this network; the listing page is), parses
title + authors + primary subject, and keeps the matches that
hit our keyword net.  State file (paper_tracker_seen.json)
remembers every ID seen, so each run reports ONLY newly-seen
matches.

Run: python paper_tracker.py [--cats quant-ph,physics.optics]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
EXP = Path(__file__).resolve().parent
OUT = EXP / "paper_tracker_matches.json"
SEEN = EXP / "paper_tracker_seen.json"

# the keyword net: broad enough to catch our lanes, specific
# enough to skip the bulk of quant-ph
NET = [r"readout", r"measurement error", r"error mitigation",
       r"calibration", r"drift", r"noise", r"error correction",
       r"compil", r"transpil", r"benchmark", r"mitigat",
       r"fidelity", r"crosstalk", r"cross talk", r"decohere",
       r"characteriz", r"qubit"]


def fetch_listing(cat: str) -> str:
    url = f"https://arxiv.org/list/{cat}/new"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (research tracker)"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_listing(html: str) -> list:
    """Entries: [(arxiv_id, title, authors, primary_subject)]."""
    out = []
    # each entry: arXiv:ID anchor ... <dd> title/authors/subjects
    for m in re.finditer(
            r'arXiv:(\d{4}\.\d{5})\s*</a>\s*\[.*?</dt>\s*<dd>(.*?)</dd>',
            html, re.S):
        aid, body = m.group(1), m.group(2)
        tm = re.search(r"list-title[^>]*>\s*(?:<span[^>]*>[^<]*</span>\s*)?"
                       r"(.*?)</div>", body, re.S)
        if not tm:
            continue
        title = re.sub(r"<[^>]+>", "", tm.group(1)).strip()
        am = re.search(r"list-authors[^>]*>(.*?)</div>", body, re.S)
        authors = re.sub(r"<[^>]+>", "", am.group(1)).strip() if am else ""
        sm = re.search(r"primary-subject[^>]*>(.*?)</span>",
                       body, re.S)
        subj = sm.group(1).strip() if sm else ""
        out.append((aid, title, authors, subj))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default="quant-ph,physics.optics")
    args = ap.parse_args()
    seen = (set(json.loads(SEEN.read_text(encoding="utf-8")))
            if SEEN.exists() else set())
    matches = []
    all_ids = []
    for cat in args.cats.split(","):
        try:
            html = fetch_listing(cat)
        except Exception as exc:
            print(f"{cat}: fetch failed: {exc}", flush=True)
            continue
        entries = parse_listing(html)
        print(f"{cat}: {len(entries)} entries", flush=True)
        for aid, title, authors, subj in entries:
            all_ids.append(aid)
            if aid in seen:
                continue
            tl = title.lower()
            if any(re.search(pat, tl) for pat in NET):
                matches.append({"arxiv": aid, "title": title,
                                "authors": authors, "subject": subj,
                                "cat": cat})
    # remember everything on the listing (so a paper that
    # scrolls off the first page is not re-reported next run)
    new_ids = [i for i in all_ids if i not in seen]
    json.dump(sorted(seen | set(all_ids)),
              open(SEEN, "w", encoding="utf-8"), indent=2)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{stamp}] {len(new_ids)} new IDs on the listings; "
          f"{len(matches)} keyword matches newly seen:")
    for m in matches:
        print(f"  {m['arxiv']}  {m['title'][:90]}  ({m['subject']})")
    OUT.write_text(json.dumps(
        {"checked_at": stamp, "new_ids": len(new_ids),
         "matches": matches}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"results -> {OUT.name}")


if __name__ == "__main__":
    main()
