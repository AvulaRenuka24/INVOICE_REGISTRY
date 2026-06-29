from rapidfuzz import fuzz


def vendor_similarity(vendor1: str, vendor2: str) -> int:
    if not vendor1 or not vendor2:
        return 0

    return fuzz.ratio(
        vendor1.upper(),
        vendor2.upper()
    )


def invoice_similarity(invoice1: str, invoice2: str) -> int:
    if not invoice1 or not invoice2:
        return 0

    return fuzz.ratio(
        invoice1.upper(),
        invoice2.upper()
    )


def is_near_duplicate(
    vendor1,
    vendor2,
    invoice1,
    invoice2,
    threshold=90
):

    vendor_score = vendor_similarity(
        vendor1,
        vendor2
    )

    invoice_score = invoice_similarity(
        invoice1,
        invoice2
    )

    return {
        "vendor_score": vendor_score,
        "invoice_score": invoice_score,
        "possible_duplicate": (
            vendor_score >= threshold
            or invoice_score >= threshold
        )
    }