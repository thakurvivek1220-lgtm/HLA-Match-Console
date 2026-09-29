"""
waitlist_ranker.py

Given one donor offer and a pool of waitlisted recipients, work out who's
eligible and rank them highest-priority-first. Uses heapq as an actual
priority queue rather than just calling sorted() on everything, partly
because the brief calls for a "priority queue sorting eligible recipients"
specifically, and partly because it means pop_next() can hand out one
candidate at a time without re-sorting the whole list, which is closer to
how an organ offer would really be worked through (offer to #1, if they
decline/are unsuitable move to #2, etc.).
"""

import heapq
from dataclasses import dataclass, field
from itertools import count
from typing import List, Optional

from match_calculator import find_contraindications, count_mismatches
from priority_scorer import score_candidate, score_breakdown
from hla_profile import DonorProfile, RecipientProfile


@dataclass
class RankedCandidate:
    recipient: RecipientProfile
    score: float
    mismatches: int
    breakdown: dict


class WaitlistRanker:
    """Wraps a heapq-based max-priority-queue of eligible recipients for a
    single donor offer.

    heapq only gives you a min-heap, so scores are pushed in negated -
    that's the usual Python trick for building a max-heap without writing
    a custom comparator.
    """

    def __init__(self, donor: DonorProfile):
        self.donor = donor
        self._heap = []
        self._tiebreak = count()  # avoids comparing RankedCandidate objects
        self.excluded: List[dict] = []  # recipients ruled out, with reasons

    def add_candidate(self, recipient: RecipientProfile) -> None:
        contraindications = find_contraindications(self.donor, recipient)
        if contraindications:
            self.excluded.append({
                "recipient": recipient,
                "reasons": contraindications,
            })
            return

        match_result = count_mismatches(self.donor, recipient)
        score = score_candidate(match_result, recipient)
        breakdown = score_breakdown(match_result, recipient)

        candidate = RankedCandidate(
            recipient=recipient,
            score=score,
            mismatches=match_result.mismatches,
            breakdown=breakdown,
        )
        # push (-score, tiebreak, candidate) so heapq behaves as a max-heap
        heapq.heappush(self._heap, (-score, next(self._tiebreak), candidate))

    def add_candidates(self, recipients: List[RecipientProfile]) -> None:
        for r in recipients:
            self.add_candidate(r)

    def pop_next(self) -> Optional[RankedCandidate]:
        """Pull the single highest-priority eligible candidate off the
        queue. Returns None once it's empty."""
        if not self._heap:
            return None
        _, _, candidate = heapq.heappop(self._heap)
        return candidate

    def ranked_list(self) -> List[RankedCandidate]:
        """Non-destructive full ranking, best match first. Useful for
        printing a report; use pop_next() instead if you actually want to
        work through offers one at a time and remove them from the queue.
        """
        snapshot = list(self._heap)
        ordered = heapq.nsmallest(len(snapshot), snapshot)
        return [candidate for _, _, candidate in ordered]

    def __len__(self):
        return len(self._heap)
