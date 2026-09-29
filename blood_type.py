"""
blood_type.py

Small helper module for ABO blood-group compatibility.

Rh factor (+/-) matters a lot for blood transfusions but for solid organ
allocation (kidneys, livers etc.) it's the ABO group that decides whether a
transplant can go ahead at all, so that's what we check here. Rh is still
stored on the profile in case someone wants to extend this later.
"""

from enum import Enum

class ABOGroup(Enum):
    O = "O"
    A = "A"
    B = "B"
    AB = "AB"

RECIPIENT_CAN_ACCEPT = {
    ABOGroup.O: {ABOGroup.O},
    ABOGroup.A: {ABOGroup.O, ABOGroup.A},
    ABOGroup.B: {ABOGroup.O, ABOGroup.B},
    ABOGroup.AB: {ABOGroup.O, ABOGroup.A, ABOGroup.B, ABOGroup.AB},
}

def is_abo_compatible(donor_group: ABOGroup, recipient_group: ABOGroup) -> bool:
    """Return True if a donor of donor_group can give an organ to a
    recipient of recipient_group, based on standard ABO rules.

    O is the universal donor, AB is the universal recipient - everything
    else follows from that.
    """
    if not isinstance(donor_group, ABOGroup) or not isinstance(recipient_group, ABOGroup):
        raise TypeError("Expected ABOGroup values for donor_group/recipient_group")

    return donor_group in RECIPIENT_CAN_ACCEPT[recipient_group]

def parse_blood_type(raw: str):
    """Turn something like 'O+' or 'ab-' typed by a user into an
    (ABOGroup, rh_positive: bool) pair.

    Accepts a bit of messiness (extra spaces, lower case) since this is the
    kind of thing that usually gets typed by hand.
    """
    if not raw:
        raise ValueError("Blood type string can't be empty")

    cleaned = raw.strip().upper()
    if cleaned.endswith("+"):
        rh_positive = True
        group_part = cleaned[:-1]
    elif cleaned.endswith("-"):
        rh_positive = False
        group_part = cleaned[:-1]
    else:
        raise ValueError(f"Couldn't find a +/- Rh sign on '{raw}'")

    try:
        group = ABOGroup(group_part)
    except ValueError as exc:
        valid = ", ".join(g.value for g in ABOGroup)
        raise ValueError(f"'{group_part}' isn't a real ABO group (expected one of {valid})") from exc

    return group, rh_positive
