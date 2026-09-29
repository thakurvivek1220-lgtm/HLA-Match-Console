"""
priority_scorer.py

Turns a MatchResult + a RecipientProfile into a single priority score, so
that candidates can be ranked against each other. The weighting below is
not taken from any real allocation policy - real systems (like UNOS's
Kidney Allocation System) use much more elaborate, regularly-reviewed
formulas. This is a simplified stand-in built for the project brief:
reward good HLA matches, reward people who've waited longer, and give
pediatric candidates a boost, which mirrors real policy in spirit even if
the exact numbers are made up.
"""

from match_calculator import MAX_MISMATCHES, MatchResult
from hla_profile import RecipientProfile

# Tunable weights - pulled out as constants instead of magic numbers
# scattered through the function, so the "policy" is easy to see and to
# change in one place (and easy to point at in the report).
POINTS_PER_AVOIDED_MISMATCH = 12      # rewards fewer mismatches
POINTS_PER_MONTH_WAITING = 1.5        # rewards time already spent waiting
MAX_WAIT_POINTS = 100                 # waiting alone can't dominate everything
PEDIATRIC_BONUS = 40
URGENCY_WEIGHT = 0.6                  # medical_urgency is already 0-100


def _wait_time_points(recipient: RecipientProfile) -> float:
    months_waited = recipient.days_on_waitlist() / 30
    points = months_waited * POINTS_PER_MONTH_WAITING
    return min(points, MAX_WAIT_POINTS)


def score_candidate(match_result: MatchResult, recipient: RecipientProfile) -> float:
    """Return a single float priority score for this recipient given a
    specific donor match. Higher = should be offered the organ sooner.

    Note this only makes sense to compare *within* the same donor offer -
    it's not a global, donor-independent ranking, since the mismatch
    component depends on which donor is being evaluated.
    """
    avoided_mismatches = MAX_MISMATCHES - match_result.mismatches
    hla_points = avoided_mismatches * POINTS_PER_AVOIDED_MISMATCH

    wait_points = _wait_time_points(recipient)
    urgency_points = recipient.medical_urgency * URGENCY_WEIGHT
    pediatric_points = PEDIATRIC_BONUS if recipient.is_pediatric else 0

    total = hla_points + wait_points + urgency_points + pediatric_points
    return round(total, 2)


def score_breakdown(match_result: MatchResult, recipient: RecipientProfile) -> dict:
    """Same as score_candidate but returns the individual components too -
    mainly so main.py can print a readable "why did this candidate rank
    where they did" explanation instead of just a single opaque number.
    """
    avoided_mismatches = MAX_MISMATCHES - match_result.mismatches
    hla_points = avoided_mismatches * POINTS_PER_AVOIDED_MISMATCH
    wait_points = round(_wait_time_points(recipient), 2)
    urgency_points = round(recipient.medical_urgency * URGENCY_WEIGHT, 2)
    pediatric_points = PEDIATRIC_BONUS if recipient.is_pediatric else 0

    return {
        "hla_points": hla_points,
        "wait_points": wait_points,
        "urgency_points": urgency_points,
        "pediatric_points": pediatric_points,
        "total": round(hla_points + wait_points + urgency_points + pediatric_points, 2),
    }
