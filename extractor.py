import pdfplumber
import re
from typing import Dict, Optional


def extract_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF.
    """

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def find_invoice_number(text: str) -> Optional[str]:

    patterns = [

        r"Invoice\s*No\.?\s*[:#]?\s*([A-Za-z0-9\-]+)",

        r"Invoice\s*Number\s*[:#]?\s*([A-Za-z0-9\-]+)",

        r"INV[- ]?\d+"

    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            if match.lastindex:
                return match.group(1)

            return match.group(0)

    return None


def find_vendor(text: str) -> Optional[str]:

    # First, look for "Vendor:"
    match = re.search(
        r"Vendor\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    # Fallback if Vendor: is missing
    skip_words = {
        "INVOICE",
        "TAX INVOICE",
        "RECEIPT",
        "BILL"
    }

    lines = text.splitlines()

    for line in lines[:15]:

        line = line.strip()

        if not line:
            continue

        if line.upper() in skip_words:
            continue

        if line.lower().startswith("invoice"):
            continue

        if line.lower().startswith("date"):
            continue

        if line.lower().startswith("total"):
            continue

        return line

    return None

def find_total_amount(text: str) -> Optional[str]:

    patterns = [

        r"Total\s*[: ]*\$?\s*([\d,]+\.\d{2})",

        r"Amount\s*Due\s*[: ]*\$?\s*([\d,]+\.\d{2})",

        r"Grand\s*Total\s*[: ]*\$?\s*([\d,]+\.\d{2})"

    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            return match.group(1)

    return None


def find_date(text: str) -> Optional[str]:

    patterns = [

        r"\d{2}/\d{2}/\d{4}",

        r"\d{4}-\d{2}-\d{2}",

        r"\d{2}-\d{2}-\d{4}"

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            return match.group(0)

    return None


def extract_invoice(pdf_path: str) -> Dict:

    text = extract_text(pdf_path)

    if not text.strip():

        raise ValueError("No text found in PDF")

    return {

        "invoice_number": find_invoice_number(text),

        "vendor_name": find_vendor(text),

        "invoice_date": find_date(text),

        "total_amount": find_total_amount(text),

        "raw_text": text

    }