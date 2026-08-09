from app.core.enums import BloodGroup

# Medical Compatibility Matrix: Key = Donor Blood Group, Value = Set of Compatible Recipient Groups
COMPATIBILITY_MATRIX: dict[str, set[str]] = {
    BloodGroup.O_NEGATIVE.value: {
        BloodGroup.O_NEGATIVE.value,
        BloodGroup.O_POSITIVE.value,
        BloodGroup.A_NEGATIVE.value,
        BloodGroup.A_POSITIVE.value,
        BloodGroup.B_NEGATIVE.value,
        BloodGroup.B_POSITIVE.value,
        BloodGroup.AB_NEGATIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },  # Universal Donor
    BloodGroup.O_POSITIVE.value: {
        BloodGroup.O_POSITIVE.value,
        BloodGroup.A_POSITIVE.value,
        BloodGroup.B_POSITIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },
    BloodGroup.A_NEGATIVE.value: {
        BloodGroup.A_NEGATIVE.value,
        BloodGroup.A_POSITIVE.value,
        BloodGroup.AB_NEGATIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },
    BloodGroup.A_POSITIVE.value: {
        BloodGroup.A_POSITIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },
    BloodGroup.B_NEGATIVE.value: {
        BloodGroup.B_NEGATIVE.value,
        BloodGroup.B_POSITIVE.value,
        BloodGroup.AB_NEGATIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },
    BloodGroup.B_POSITIVE.value: {
        BloodGroup.B_POSITIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },
    BloodGroup.AB_NEGATIVE.value: {
        BloodGroup.AB_NEGATIVE.value,
        BloodGroup.AB_POSITIVE.value,
    },
    BloodGroup.AB_POSITIVE.value: {
        BloodGroup.AB_POSITIVE.value,
    },  # Recipient Universal Only
}


def is_blood_compatible(donor_group: str, recipient_group: str) -> bool:
    """Checks if a donor's blood group is medically compatible with a recipient's blood group."""
    compatible_recipients = COMPATIBILITY_MATRIX.get(donor_group, set())
    return recipient_group in compatible_recipients


def get_compatible_donor_groups(recipient_group: str) -> set[str]:
    """Returns the set of all donor blood groups that can donate to the given recipient blood group."""
    compatible_donors = set()
    for donor_grp, recipient_set in COMPATIBILITY_MATRIX.items():
        if recipient_group in recipient_set:
            compatible_donors.add(donor_grp)
    return compatible_donors
