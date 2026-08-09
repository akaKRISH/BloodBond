import pytest
from app.services.blood_matching import is_blood_compatible, get_compatible_donor_groups
from app.core.enums import BloodGroup


def test_universal_donor_o_negative():
    # O- can donate to all 8 blood groups
    all_groups = [g.value for g in BloodGroup]
    for recipient in all_groups:
        assert is_blood_compatible("O-", recipient) is True


def test_universal_recipient_ab_positive():
    # AB+ recipient can receive from all 8 blood groups
    all_groups = [g.value for g in BloodGroup]
    for donor in all_groups:
        assert is_blood_compatible(donor, "AB+") is True


def test_incompatible_combinations():
    # A+ cannot donate to O-
    assert is_blood_compatible("A+", "O-") is False
    # B+ cannot donate to A+
    assert is_blood_compatible("B+", "A+") is False
    # AB+ cannot donate to O+
    assert is_blood_compatible("AB+", "O+") is False


def test_get_compatible_donor_groups():
    # O+ recipient can receive from O- and O+
    donors_for_o_pos = get_compatible_donor_groups("O+")
    assert donors_for_o_pos == {"O-", "O+"}

    # B- recipient can receive from O- and B-
    donors_for_b_neg = get_compatible_donor_groups("B-")
    assert donors_for_b_neg == {"O-", "B-"}
