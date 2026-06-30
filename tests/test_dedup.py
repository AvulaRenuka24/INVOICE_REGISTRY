from fuzzy import is_near_duplicate


def test_same_invoice():

    result = is_near_duplicate(
        "Amazon",
        "Amazon",
        "INV-100",
        "INV-100"
    )

    assert result["possible_duplicate"] == True


def test_vendor_typo():

    result = is_near_duplicate(
        "Microsoft",
        "Micro Soft",
        "INV-200",
        "INV-200"
    )

    assert result["possible_duplicate"] == True


def test_different_invoice():

    result = is_near_duplicate(
        "Amazon",
        "Google",
        "INV-100",
        "INV-999"
    )

    assert result["possible_duplicate"] == False