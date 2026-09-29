"""
hla_profile.py

Holds the immunology data we need per person - both donors and recipients
end up using the same HLAProfile shape, with a couple of recipient-only
fields (wait time, pediatric flag, urgency, PRA) added on RecipientProfile.

A real transplant registry tracks way more loci and sub-typing detail than
this (HLA-A, -B, -C, -DR, -DQ, -DP...), but the brief calls out HLA-A, -B
and -DR specifically, each with two alleles (one inherited from each
parent), so that's what's modelled here - six values total per person,
which lines up with the "0 to 6 mismatches" scoring described in the
project spec.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Tuple

from blood_type import ABOGroup, parse_blood_type

def _validate_allele_pair(locus_name: str, alleles: Tuple[str, str]) -> None:
    if not isinstance(alleles, (tuple, list)) or len(alleles) != 2:
        raise ValueError(f"{locus_name} needs exactly two alleles, got {alleles!r}")
    for a in alleles:
        if not a or not isinstance(a, str):
            raise ValueError(f"{locus_name} allele can't be blank ({alleles!r})")

@dataclass
class HLAProfile:
    """Base immunology profile shared by donors and recipients.

    hla_a / hla_b / hla_dr are each a 2-tuple of allele codes, e.g.
    ("A2", "A24"). Real HLA typing uses codes like "A*02:01" - I kept the
    format loose on purpose (plain strings) so the matching logic doesn't
    care about the exact nomenclature used.
    """

    person_id: str
    name: str
    blood_type_raw: str
    hla_a: Tuple[str, str]
    hla_b: Tuple[str, str]
    hla_dr: Tuple[str, str]
    rh_positive: bool = field(init=False, default=True)
    blood_group: ABOGroup = field(init=False, default=None)

    def __post_init__(self):
        if not self.person_id:
            raise ValueError("person_id is required")
        _validate_allele_pair("HLA-A", self.hla_a)
        _validate_allele_pair("HLA-B", self.hla_b)
        _validate_allele_pair("HLA-DR", self.hla_dr)

        group, rh = parse_blood_type(self.blood_type_raw)
        self.blood_group = group
        self.rh_positive = rh

    def loci(self):
        """Convenience accessor - iterate over (locus_name, alleles)."""
        return (
            ("HLA-A", self.hla_a),
            ("HLA-B", self.hla_b),
            ("HLA-DR", self.hla_dr),
        )

    def __str__(self):
        return f"{self.name} ({self.person_id}) - {self.blood_type_raw}"

@dataclass
class DonorProfile(HLAProfile):
    """A deceased or living donor. organ_type is just descriptive text for
    now (e.g. 'kidney') - the matching logic doesn't branch on it, but it's
    useful in reports and would matter if this were extended to multiple
    organ types with different rules.
    """

    organ_type: str = "kidney"

@dataclass
class RecipientProfile(HLAProfile):
    """A waitlist candidate, with the extra fields the priority queue
    needs: how long they've been waiting, whether they're a pediatric
    case, a 0-100 medical urgency score, and panel-reactive antibody (PRA)
    percentage, which feeds into the crossmatch/contraindication check.
    """

    waitlist_date: date = field(default_factory=date.today)
    is_pediatric: bool = False
    medical_urgency: int = 50
    pra_percent: int = 0

    def __post_init__(self):
        super().__post_init__()
        if not (0 <= self.medical_urgency <= 100):
            raise ValueError("medical_urgency must be between 0 and 100")
        if not (0 <= self.pra_percent <= 100):
            raise ValueError("pra_percent must be between 0 and 100")

    def days_on_waitlist(self, as_of: date = None) -> int:
        as_of = as_of or date.today()
        delta = as_of - self.waitlist_date
        return max(delta.days, 0)
