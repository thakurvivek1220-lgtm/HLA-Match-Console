"""
main.py

Small interactive demo of the whole pipeline: pick a donor offer, run it
against the sample waitlist, and print a ranked report of who should be
considered first (and who's excluded, and why).

Run it with:
    python main.py

or, if double-clicking / hitting "Run" in your editor:
    just run this file directly - it doesn't need to be run as a module,
    there's no package structure to worry about here.

Pass --auto to skip the donor-selection prompt and just run against the
first sample donor (handy for quick testing).
"""

import argparse
import sys

from waitlist_ranker import WaitlistRanker
from sample_data import sample_donors, sample_recipients


def print_header(text: str) -> None:
    print()
    print(text)
    print("-" * len(text))


def choose_donor(donors, auto: bool):
    if auto:
        return donors[0]

    print_header("Available donor offers")
    for i, d in enumerate(donors, start=1):
        print(f"  {i}. {d} - HLA-A {d.hla_a}, HLA-B {d.hla_b}, HLA-DR {d.hla_dr}")

    while True:
        choice = input(f"Pick a donor (1-{len(donors)}): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(donors)):
            print("That's not one of the options, try again.")
            continue
        return donors[int(choice) - 1]


def run_offer(donor, recipients):
    ranker = WaitlistRanker(donor)
    ranker.add_candidates(recipients)

    print_header(f"Ranked candidates for {donor} ({donor.organ_type})")
    ranked = ranker.ranked_list()
    if not ranked:
        print("No eligible recipients on the waitlist for this donor.")
    else:
        for rank, candidate in enumerate(ranked, start=1):
            r = candidate.recipient
            print(
                f"  #{rank}  {r.name:<24} score={candidate.score:<7} "
                f"mismatches={candidate.mismatches}/6  "
                f"(HLA {candidate.breakdown['hla_points']}, "
                f"wait {candidate.breakdown['wait_points']}, "
                f"urgency {candidate.breakdown['urgency_points']}, "
                f"pediatric {candidate.breakdown['pediatric_points']})"
            )

    if ranker.excluded:
        print_header("Excluded from consideration")
        for entry in ranker.excluded:
            r = entry["recipient"]
            print(f"  {r.name}:")
            for reason in entry["reasons"]:
                print(f"    - {reason}")

    return ranker


def main(argv=None):
    parser = argparse.ArgumentParser(description="Organ donor-recipient HLA compatibility scorer")
    parser.add_argument("--auto", action="store_true", help="skip the prompt, use the first sample donor")
    args = parser.parse_args(argv)

    donors = sample_donors()
    recipients = sample_recipients()

    try:
        donor = choose_donor(donors, args.auto)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(1)

    run_offer(donor, recipients)


if __name__ == "__main__":
    main()
