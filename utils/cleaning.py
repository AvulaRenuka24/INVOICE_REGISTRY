import re
from dateutil import parser

# Common company suffixes to remove
COMPANY_SUFFIXES = [
    "INC", "LLC", "LTD", "LIMITED", "CORP", "CORPORATION", "CO"
]


def normalize_vendor(vendor: str) -> str:
    """
    Normalize vendor names for duplicate detection.
    Example:
    'Acme, Inc.' -> 'ACME'
    ' Acme LLC ' -> 'ACME'
    """
    if not vendor:
        return "UNKNOWN"

    vendor = vendor.upper().strip()

    # Remove punctuation
    vendor = re.sub(r"[^\w\s]", "", vendor)

    # Remove common company suffixes
    words = vendor.split()
    words = [w for w in words if w not in COMPANY_SUFFIXES]

    # Remove extra spaces
    vendor = " ".join(words)

    return vendor


def parse_date(date_str: str):
    """
    Parse different date formats using python-dateutil.
    Examples:
    28/06/2026
    2026-06-28
    June 28, 2026
    """
    if not date_str:
        return None

    try:
        return parser.parse(date_str)
    except Exception:
        return None


def parse_amount(amount_str: str):
    """
    Parse different currency formats.

    Examples:
    $1,234.50
    INR 12,500
    EUR 750,24
    """

    if not amount_str:
        return None

    amount = amount_str.strip()

    # Handle European decimal format
    if "," in amount and "." not in amount:
        amount = amount.replace(",", ".")

    # Remove currency symbols and letters
    amount = re.sub(r"[^\d.,-]", "", amount)

    # Remove thousand separators
    if "," in amount and "." in amount:
        amount = amount.replace(",", "")

    try:
        return float(amount)
    except Exception:
        return None