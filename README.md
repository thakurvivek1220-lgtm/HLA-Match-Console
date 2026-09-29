# Organ Donor-Recipient HLA Compatibility Scorer

A small Python engine that evaluates a donor organ against a waitlist of
recipients: it scores HLA (tissue-type) compatibility, screens out unsafe
pairings on blood type and sensitization grounds, and ranks the remaining
eligible candidates by priority.

Built as a course project — not a clinical tool. See
[`statement.md`](statement.md) for the problem statement and scope.

## Overview

Real organ allocation checks three things before an offer can go ahead:
tissue-type (HLA) match quality, blood-type compatibility, and whether the
recipient's immune system is likely to attack the new organ. This project
models a simplified version of that pipeline for a single donor offer at
a time, and produces a ranked list of who should be considered first.

## Features

- **HLA mismatch scoring** across HLA-A, HLA-B and HLA-DR (0–6 scale),
  correctly handling homozygous donors so a repeated allele isn't
  double-counted.
- **ABO blood-type compatibility check**, plus a high-PRA (panel reactive
  antibody) sensitization check — either one rules a pairing out entirely,
  independent of how good the HLA match looks.
- **Priority-queue waitlist ranking** (built on `heapq`) that scores each
  eligible recipient on HLA quality, time already spent waiting, medical
  urgency, and a pediatric-candidate bonus, then ranks them highest
  priority first. Recipients who fail a hard check (blood type, PRA) are
  reported separately with the reason, rather than just being scored low.
- **Interactive CLI demo** (`main.py`) that lets you pick a sample donor
  offer and prints a readable ranked report, including a point-by-point
  breakdown of each score.

## Technologies / Tools Used

- Python 3.10+ (standard library only — `dataclasses`, `heapq`,
  `argparse`, `enum`; no external runtime dependencies)
- `pytest` for the test suite
- Git for version control

## Project Structure

Deliberately flat — every module sits in the same folder as `main.py`, so
there's no package/import path to get wrong. Just open the folder and run
it.

```
organ-match/
├── main.py                # interactive CLI entry point - run this
├── hla_profile.py          # HLAProfile / DonorProfile / RecipientProfile
├── blood_type.py           # ABOGroup + ABO compatibility rules
├── match_calculator.py     # HLA mismatch scoring + contraindication checks
├── priority_scorer.py      # priority point formula
├── waitlist_ranker.py      # heapq-based priority queue / ranking
├── sample_data.py          # sample donors & recipients for the demo
├── tests/
│   ├── conftest.py         # lets the tests import the modules above
│   ├── test_blood_type.py
│   ├── test_match_calculator.py
│   └── test_waitlist_ranker.py
├── statement.md
├── requirements.txt
└── README.md
```

## Install & Run

1. Unzip the project and open **the folder that contains `main.py`**
   (i.e. this folder itself, not a parent or a subfolder of it) in your
   editor/terminal.
2. (Optional but recommended) create a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install the one dev dependency (only needed for running tests):
   ```bash
   pip install -r requirements.txt
   ```
4. Run it:
   ```bash
   python main.py
   ```
   or skip the donor-selection prompt:
   ```bash
   python main.py --auto
   ```

There's nothing else to configure — no database, no environment
variables, no package to install for the app itself. If `python` isn't
recognized on Windows, try `py main.py` instead.

## Testing

```bash
pytest tests/ -v
```

The suite covers:

- ABO compatibility rules and blood-type string parsing (including bad
  input)
- HLA mismatch math — perfect matches, partial matches, full mismatches,
  and the homozygous-donor edge case
- Contraindication detection (ABO mismatch, high PRA)
- Waitlist ranking — correct ordering by score, exclusion of unsafe
  pairs, the pediatric bonus, and priority-queue draining via `pop_next()`

## Screenshots

Sample CLI output (`python main.py --auto`):

```
Ranked candidates for Donor A (D-001) - O+ (kidney)
---------------------------------------------------
  #1  Recipient 3 (pediatric)  score=161.6   mismatches=3/6  (HLA 36, wait 49.6, urgency 36.0, pediatric 40)
  #2  Recipient 2              score=160.0   mismatches=3/6  (HLA 36, wait 100, urgency 24.0, pediatric 0)
  #3  Recipient 1              score=150.75  mismatches=2/6  (HLA 48, wait 60.75, urgency 42.0, pediatric 0)
  #4  Recipient 5              score=144.75  mismatches=3/6  (HLA 36, wait 75.75, urgency 33.0, pediatric 0)

Excluded from consideration
---------------------------
  Recipient 4:
    - High sensitization risk: recipient PRA is 90%, positive crossmatch likely (threshold 80%)
```

## Notes / Limitations

- The priority formula (weights in `priority_scorer.py`) is a simplified
  approximation built for this project, not a real clinical allocation
  policy — real systems like UNOS's Kidney Allocation System are far more
  elaborate and are reviewed by policy bodies, not hard-coded constants.
- PRA is used here as a stand-in for an actual laboratory crossmatch
  result, which this project doesn't otherwise model.
- Everything runs in-memory against sample data; there's no persistence
  layer, since the brief didn't call for one.

## If something still won't run

This project has no package structure to trip over, so the only two
things that usually go wrong are:

1. **Wrong folder opened.** Make sure `main.py` and `hla_profile.py`
   (etc.) are directly visible in your file explorer/sidebar — not nested
   one level deeper inside another `organ-match` folder from a double
   extraction.
2. **Wrong Python.** Run `python --version` (needs 3.10+) — on some
   systems you may need `python3` or `py` instead of `python`.
