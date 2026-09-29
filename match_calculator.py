"""
match_calculator.py

Two jobs live here:

1. count_mismatches() - the actual HLA mismatch score (0-6), comparing
   donor vs recipient allele-by-allele across the three loci.
2. find_contraindications() - "hard stop" checks that make a match unsafe
   no matter how good the HLA score looks (wrong blood type, high-risk
   crossmatch). These are kept separate from the mismatch score on purpose:
   a mismatch score is a *quality* measure, a contraindication is a
   *safety* gate, and mixing the two together made the ranking logic
   confusing when I first tried it as a single number.
"""

from dataclasses import dataclass, field
from typing import List

from blood_type import is_abo_compatible
from hla_profile import DonorProfile, RecipientProfile

# Above this PRA percentage we flag a positive-crossmatch risk. In real
# life this would come from an actual lab crossmatch test, not just the
# PRA number, but PRA is a reasonable stand-in for "how sensitized is this
# patient's immune system" for a project like this.
HIGH_PRA_THRESHOLD = 80

MAX_MISMATCHES = 6


@dataclass
class MatchResult:
    donor_id: str
    recipient_id: str
    mismatches: int
    mismatch_breakdown: dict
    contraindications: List[str] = field(default_factory=list)

    @property
    def is_viable(self) -> bool:
        """A match is viable if there's nothing on the contraindication
        list - the mismatch count on its own never disqualifies a match,
        it just makes it a lower-quality one."""
        return len(self.contraindications) == 0


def _count_locus_mismatches(donor_alleles, recipient_alleles) -> int:
    """How many of the donor's two alleles at this locus are NOT found in
    the recipient's two alleles. Standard way of scoring a single HLA
    locus - result is 0, 1 or 2.

    Using a list (not a set) for the "remaining" recipient alleles so that
    a homozygous donor (same allele twice, e.g. A2/A2) can't double-count
    against a recipient who only actually carries that allele once.
    """
    remaining_recipient = list(recipient_alleles)
    mismatches = 0
    for allele in donor_alleles:
        if allele in remaining_recipient:
            remaining_recipient.remove(allele)
        else:
            mismatches += 1
    return mismatches


def count_mismatches(donor: DonorProfile, recipient: RecipientProfile) -> "MatchResult":
    """Compare all three loci and build the full MatchResult, mismatch
    score included. Doesn't decide viability by itself - call
    find_contraindications() (or just use match(), below, which does
    both) to get the safety checks too.
    """
    breakdown = {}
    total = 0
    for locus_name, donor_alleles in donor.loci():
        recipient_alleles = dict(recipient.loci())[locus_name]
        locus_mismatches = _count_locus_mismatches(donor_alleles, recipient_alleles)
        breakdown[locus_name] = locus_mismatches
        total += locus_mismatches

    assert 0 <= total <= MAX_MISMATCHES, f"mismatch total out of range: {total}"

    return MatchResult(
        donor_id=donor.person_id,
        recipient_id=recipient.person_id,
        mismatches=total,
        mismatch_breakdown=breakdown,
    )


def find_contraindications(donor: DonorProfile, recipient: RecipientProfile) -> List[str]:
    """Absolute reasons this donor/recipient pair should not go ahead,
    regardless of how few HLA mismatches there are. Returns a plain list
    of human-readable reasons (empty list = nothing blocking it).
    """
    reasons = []

    if not is_abo_compatible(donor.blood_group, recipient.blood_group):
        reasons.append(
            f"ABO incompatible: donor is {donor.blood_group.value}, "
            f"recipient is {recipient.blood_group.value}"
        )

    if recipient.pra_percent >= HIGH_PRA_THRESHOLD:
        reasons.append(
            f"High sensitization risk: recipient PRA is {recipient.pra_percent}%, "
            f"positive crossmatch likely (threshold {HIGH_PRA_THRESHOLD}%)"
        )

    return reasons


def match(donor: DonorProfile, recipient: RecipientProfile) -> MatchResult:
    """Convenience wrapper - run the mismatch score and the
    contraindication checks together and hand back one MatchResult.
    """
    result = count_mismatches(donor, recipient)
    result.contraindications = find_contraindications(donor, recipient)
    return result
