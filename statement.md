# Project Statement

## Problem Statement

Matching a donated organ to the right recipient is a race against time and
biology. Transplant teams have to check Human Leukocyte Antigen (HLA)
markers across three key loci (HLA-A, HLA-B, HLA-DR), confirm ABO blood
type compatibility, and screen out patients whose immune system is likely
to reject the organ outright — all before the organ is no longer viable.
Getting any of that wrong risks acute graft rejection or a wasted organ
that could have gone to someone else on the list.

## Scope

This project is a simplified organ donor-recipient matching engine for a
single organ offer at a time (kidney, by default, though nothing in the
matching logic is kidney-specific). Given one donor and a pool of
waitlisted recipients, it:

- Scores HLA compatibility across the six alleles (HLA-A ×2, HLA-B ×2,
  HLA-DR ×2), producing a 0–6 mismatch count.
- Checks ABO blood type compatibility and flags a high sensitization
  (PRA) risk as an absolute contraindication.
- Ranks the remaining eligible recipients using a priority score that
  combines HLA match quality, time spent waiting, medical urgency, and a
  pediatric-candidate bonus.

It does not attempt to model the full complexity of a real allocation
system (e.g. UNOS's Kidney Allocation System) — the priority formula is a
simplified, project-scale approximation of real policy goals, not a
clinical tool.

## Target Users

- Students/instructors evaluating the project against the course rubric.
- Hypothetically, transplant coordinators as a first-pass triage/decision
  support tool — sitting alongside, not replacing, an actual clinical and
  laboratory crossmatch workflow.

## High-Level Features

1. **HLA compatibility scoring** — `hla_profile.py` + `match_calculator.py`
2. **Blood type / contraindication screening** — `blood_type.py` +
   `match_calculator.py`
3. **Priority-based waitlist ranking** — `priority_scorer.py` +
   `waitlist_ranker.py`, exposed through an interactive CLI in `main.py`
