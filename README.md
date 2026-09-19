# paper-tracker

A zero-dependency Python script that sweeps the arXiv new listings and
reports papers matching your keyword net — built for tracking the
quantum **readout / measurement-error / calibration / drift / compiler /
benchmark / error-mitigation** lanes.

No API key, no external libraries (stdlib `urllib` only). State is two
JSON files next to the script; every run only reports **newly-seen**
matches.

## Quick start

```bash
python paper_tracker.py                 # quant-ph + physics.optics
python paper_tracker.py --cats quant-ph # just quant-ph
```

First run downloads today's listing pages, prints every matching paper
(with arXiv ID, title, authors, primary subject), and writes:

- `paper_tracker_matches.json` — the latest sweep: `checked_at`,
  `new_ids` (listing IDs never seen before), `matches` (title/keyword
  hits with metadata)
- `paper_tracker_seen.json` — the ID memory (auto-created); papers are
  only reported once, even after they scroll off the first listing page

## Customizing the keyword net

Edit the `NET` list at the top of `paper_tracker.py` — plain regex
patterns matched against the lowercased title:

```python
NET = [r"readout", r"measurement error", r"error mitigation",
       r"calibration", r"drift", r"noise", r"error correction",
       r"compil", r"transpil", r"benchmark", r"mitigat",
       r"fidelity", r"crosstalk", r"cross talk", r"decohere",
       r"characteriz", r"qubit"]
```

## Running it on a schedule (optional)

The script is one-shot by design; pair it with any scheduler, e.g.
Windows Task Scheduler daily at 09:00, or cron:

```cron
0 9 * * * cd /path/to/paper-tracker && python3 paper_tracker.py >> tracker.log 2>&1
```

## Notes

- The parser targets the arXiv **new-listing HTML pages**
  (`arxiv.org/list/<cat>/new`) — kept deliberately dependency-free.
  If arXiv changes the page markup, `parse_listing` is the function
  to adjust.
- The arXiv export API is used by many tools; this project avoids it
  because the listing page is reachable from restricted networks.

## License

MIT — see [LICENSE](LICENSE). Not affiliated with arXiv.
