"""
sample_data.py

Hand-typed sample donors/recipients so main.py has something to run
against without needing a database or a CSV import. Numbers and allele
codes are made up for demo purposes - none of this is real patient data.
"""

from datetime import date

from hla_profile import DonorProfile, RecipientProfile


def sample_donors():
    return [
        DonorProfile(
            person_id="D-001",
            name="Donor A",
            blood_type_raw="O+",
            hla_a=("A1", "A2"),
            hla_b=("B7", "B8"),
            hla_dr=("DR3", "DR4"),
            organ_type="kidney",
        ),
        DonorProfile(
            person_id="D-002",
            name="Donor B",
            blood_type_raw="AB-",
            hla_a=("A2", "A24"),
            hla_b=("B44", "B62"),
            hla_dr=("DR1", "DR15"),
            organ_type="kidney",
        ),
    ]


def sample_recipients():
    return [
        RecipientProfile(
            person_id="R-001",
            name="Recipient 1",
            blood_type_raw="O+",
            hla_a=("A1", "A2"),
            hla_b=("B7", "B44"),
            hla_dr=("DR3", "DR15"),
            waitlist_date=date(2023, 6, 1),
            is_pediatric=False,
            medical_urgency=70,
            pra_percent=10,
        ),
        RecipientProfile(
            person_id="R-002",
            name="Recipient 2",
            blood_type_raw="A+",
            hla_a=("A2", "A24"),
            hla_b=("B8", "B62"),
            hla_dr=("DR4", "DR1"),
            waitlist_date=date(2021, 3, 15),
            is_pediatric=False,
            medical_urgency=40,
            pra_percent=5,
        ),
        RecipientProfile(
            person_id="R-003",
            name="Recipient 3 (pediatric)",
            blood_type_raw="O-",
            hla_a=("A1", "A3"),
            hla_b=("B7", "B27"),
            hla_dr=("DR3", "DR7"),
            waitlist_date=date(2024, 1, 10),
            is_pediatric=True,
            medical_urgency=60,
            pra_percent=15,
        ),
        RecipientProfile(
            person_id="R-004",
            name="Recipient 4",
            blood_type_raw="B+",
            hla_a=("A9", "A11"),
            hla_b=("B12", "B18"),
            hla_dr=("DR11", "DR13"),
            waitlist_date=date(2020, 11, 20),
            is_pediatric=False,
            medical_urgency=85,
            pra_percent=90,  # deliberately high, should get flagged
        ),
        RecipientProfile(
            person_id="R-005",
            name="Recipient 5",
            blood_type_raw="AB+",
            hla_a=("A2", "A2"),
            hla_b=("B44", "B7"),
            hla_dr=("DR15", "DR3"),
            waitlist_date=date(2022, 8, 5),
            is_pediatric=False,
            medical_urgency=55,
            pra_percent=20,
        ),
    ]
