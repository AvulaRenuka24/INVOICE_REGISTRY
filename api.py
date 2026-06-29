import os
import csv
import io
from datetime import datetime
from db import DuplicateCandidate

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from sqlalchemy import bindparam

from db import (
    init_db,
    SessionLocal,
    Document,
    Invoice,
    DuplicateCandidate
)

from extractor import extract_invoice

from fuzzy import is_near_duplicate

from utils.cleaning import (
    normalize_vendor,
    parse_date,
    parse_amount
)

from utils.hashing import sha256_bytes

from utils.logging_config import logger


app = FastAPI(
    title="Invoice Registry API",
    version="1.0"
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>

    <head>
        <title>Invoice Registry</title>
    </head>

    <body style="font-family:Arial;padding:40px">

        <h1>Invoice Registry API</h1>

        <h2>Internship Assignment</h2>

        <ul>

            <li>Upload Invoice</li>

            <li>Duplicate Detection</li>

            <li>Search</li>

            <li>Soft Delete</li>

            <li>Review</li>

            <li>CSV Export</li>

        </ul>

        <a href="/docs">

        Swagger UI

        </a>

    </body>

    </html>

    """


@app.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):

    db = SessionLocal()

    content = await file.read()

    sha256 = sha256_bytes(content)

    duplicate = (
        db.query(Document)
        .filter(Document.sha256 == sha256)
        .first()
    )

    if duplicate:

        raise HTTPException(

            status_code=409,

            detail={

                "message": "Duplicate file",

                "document_id": duplicate.id,

                "uploaded_at": duplicate.uploaded_at

            }

        )

    save_path = os.path.join(

        UPLOAD_FOLDER,

        file.filename

    )

    with open(save_path, "wb") as pdf:

        pdf.write(content)
    try:

        data = extract_invoice(save_path)

        vendor = normalize_vendor(
            data["vendor_name"]
        )

        existing_invoice = (
            db.query(Invoice)
            .filter(
                Invoice.vendor_normalized == vendor,
                Invoice.invoice_number == data["invoice_number"]
            )
            .first()
        )

        if existing_invoice:

            invoice = existing_invoice

            invoice_status = "existing"

        else:

            invoice = Invoice(

                invoice_number=data["invoice_number"],

                vendor_name=data["vendor_name"],

                vendor_normalized=vendor,

                invoice_date=parse_date(
                    data["invoice_date"]
                ),

                total_amount=parse_amount(
                    data["total_amount"]
                ),

                currency="USD"

            )

            db.add(invoice)

            db.flush()

            invoice_status = "new"

        document = Document(

            filename=file.filename,

            size_bytes=len(content),

            sha256=sha256,

            status="processed",

            doc_type="pdf"

        )

        document.invoices.append(invoice)

        db.add(document)

        db.commit()

        db.refresh(document)

        db.refresh(invoice)

        logger.info(
            f"{file.filename} uploaded"
        )

        return {

            "status": "success",

            "document_id": document.id,

            "invoice_id": invoice.id,

            "invoice_status": invoice_status

        }

    except Exception as e:

        failed = Document(

            filename=file.filename,

            size_bytes=len(content),

            sha256=sha256,

            status="failed",

            failure_reason=str(e),

            doc_type="pdf"

        )

        db.add(failed)

        db.commit()

        logger.error(str(e))

        raise HTTPException(

            status_code=400,

            detail=str(e)

        )
       
# ===========================
# DOCUMENT ENDPOINTS
# ===========================

@app.get("/documents")
def get_documents(status: str | None = None):

    db = SessionLocal()

    query = db.query(Document)

    if status is not None:
        query = query.filter(Document.status == status)

    return query.all()


@app.get("/documents/{document_id}")
def get_document(document_id: int):

    db = SessionLocal()

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# ===========================
# INVOICE LIST
# ===========================

@app.get("/invoices")
def list_invoices(

    limit: int = Query(20),

    offset: int = Query(0),

    vendor: str | None = None,

    invoice_number: str | None = None,

    currency: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None,

    min_amount: float | None = None,

    max_amount: float | None = None

):

    db = SessionLocal()

    query = db.query(Invoice)

    query = query.filter(
        Invoice.deleted_at == None
    )

    if vendor:

        pattern = "%" + vendor.upper() + "%"

        query = query.filter(
            Invoice.vendor_normalized.like(
                bindparam(
                    "vendor_pattern",
                    value=pattern
                )
            )
        )

    if invoice_number:

        pattern = "%" + invoice_number + "%"

        query = query.filter(
            Invoice.invoice_number.like(
                bindparam(
                    "invoice_pattern",
                    value=pattern
                )
            )
        )

    if currency:

        query = query.filter(
            Invoice.currency == currency
        )

    if start_date:

        start = parse_date(start_date)

        if start:

            query = query.filter(
                Invoice.invoice_date >= start
            )

    if end_date:

        end = parse_date(end_date)

        if end:

            query = query.filter(
                Invoice.invoice_date <= end
            )

    if min_amount is not None:

        query = query.filter(
            Invoice.total_amount >= min_amount
        )

    if max_amount is not None:

        query = query.filter(
            Invoice.total_amount <= max_amount
        )

    total = query.count()

    invoices = (

        query

        .offset(offset)

        .limit(limit)

        .all()

    )

    return {

        "total": total,

        "limit": limit,

        "offset": offset,

        "results": invoices

    }


@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int):

    db = SessionLocal()

    invoice = (

        db.query(Invoice)

        .filter(Invoice.id == invoice_id)

        .first()

    )

    if not invoice:

        raise HTTPException(

            status_code=404,

            detail="Invoice not found"

        )

    return invoice


# ===========================
# SOFT DELETE
# ===========================

@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int):

    db = SessionLocal()

    invoice = (

        db.query(Invoice)

        .filter(Invoice.id == invoice_id)

        .first()

    )

    if invoice is None:

        raise HTTPException(

            status_code=404,

            detail="Invoice not found"

        )

    invoice.deleted_at = datetime.utcnow()

    db.commit()

    return {

        "message": "Invoice soft deleted"

    }


# ===========================
# STATS
# ===========================
@app.get("/stats")
def stats():

    db = SessionLocal()

    total_documents = db.query(Document).count()

    total_invoices = db.query(Invoice).count()

    processed = (

        db.query(Document)

        .filter(Document.status == "processed")

        .count()

    )

    failed = (

        db.query(Document)

        .filter(Document.status == "failed")

        .count()

    )

    duplicate_files = (
        db.query(Document)
        .filter(Document.status == "duplicate")
        .count()
    )

    duplicate_invoices = (
        db.query(Invoice)
        .filter(Invoice.review_status == "merged")
        .count()
    )

    return {

        "documents": total_documents,

        "processed_documents": processed,

        "failed_documents": failed,

        "unique_invoices": total_invoices,

        "duplicate_files_blocked": duplicate_files,

        "duplicate_invoices_caught": duplicate_invoices

    }

# ===========================
# UPDATE REVIEW STATUS
# ===========================

@app.patch("/invoices/{invoice_id}")
def update_invoice(
    invoice_id: int,
    vendor_name: str | None = None,
    invoice_number: str | None = None,
    invoice_date: str | None = None,
    total_amount: str | None = None,
    currency: str | None = None,
    review_status: str | None = None
):

    db = SessionLocal()

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    if vendor_name is not None:
        invoice.vendor_name = vendor_name
        invoice.vendor_normalized = normalize_vendor(vendor_name)

    if invoice_number is not None:
        invoice.invoice_number = invoice_number

    if invoice_date is not None:
        parsed = parse_date(invoice_date)
        if parsed:
            invoice.invoice_date = parsed

    if total_amount is not None:
        parsed = parse_amount(total_amount)
        if parsed is not None:
            invoice.total_amount = parsed

    if currency is not None:
        invoice.currency = currency

    if review_status is not None:
        invoice.review_status = review_status

    db.commit()

    db.refresh(invoice)

    return invoice

# ===========================
# DUPLICATE REVIEW
# ===========================

@app.get("/duplicates")
def duplicate_candidates():

    db = SessionLocal()

    try:

        invoices = (
            db.query(Invoice)
            .filter(Invoice.deleted_at == None)
            .all()
        )

        db.query(DuplicateCandidate).delete()
        db.commit()

        for i in range(len(invoices)):
            for j in range(i + 1, len(invoices)):

                # Compare only plausible pairs
                if (
                    invoices[i].invoice_date != invoices[j].invoice_date
                    and
                    invoices[i].total_amount != invoices[j].total_amount
                ):
                    continue

                comparison = is_near_duplicate(

                    invoices[i].vendor_normalized,
                    invoices[j].vendor_normalized,

                    invoices[i].invoice_number,
                    invoices[j].invoice_number

                )

                if comparison["possible_duplicate"]:

                    candidate = DuplicateCandidate(

                        invoice1_id=invoices[i].id,
                        invoice2_id=invoices[j].id,

                        vendor_score=comparison["vendor_score"],
                        invoice_score=comparison["invoice_score"],

                        status="pending"

                    )

                    db.add(candidate)

        db.commit()

        return db.query(DuplicateCandidate).all()

    finally:
        db.close()

# RESOLVE DUPLICATES
@app.post("/duplicates/{candidate_id}/resolve")
def resolve_duplicate(
    candidate_id: int,
    action: str
):

    db = SessionLocal()

    candidate = (
        db.query(DuplicateCandidate)
        .filter(DuplicateCandidate.id == candidate_id)
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Duplicate candidate not found"
        )

    if action == "not_duplicate":

        candidate.status = "not_duplicate"

        db.commit()

        return {
            "message": "Marked as not duplicate"
        }

    if action == "merge":

        winner = (
            db.query(Invoice)
            .filter(Invoice.id == candidate.invoice1_id)
            .first()
        )

        loser = (
            db.query(Invoice)
            .filter(Invoice.id == candidate.invoice2_id)
            .first()
        )

        if winner is None or loser is None:
            raise HTTPException(
                status_code=404,
                detail="Invoice not found"
            )

        for document in loser.documents:
            if document not in winner.documents:
                winner.documents.append(document)

        loser.review_status = "merged"

        candidate.status = "merged"

        db.commit()

        return {
            "message": "Invoices merged"
        }

    raise HTTPException(
        status_code=400,
        detail="Action must be merge or not_duplicate"
    )


# ===========================
# EXPORT CSV
# ===========================
@app.get("/export")
def export_csv(

    vendor: str | None = None,

    currency: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None,

    min_amount: float | None = None,

    max_amount: float | None = None

):

    db = SessionLocal()

    query = db.query(Invoice)

    query = query.filter(
        Invoice.deleted_at == None
    )

    query = query.filter(
        Invoice.review_status != "merged"
    )

    if vendor:

        pattern = "%" + vendor.upper() + "%"

        query = query.filter(
            Invoice.vendor_normalized.like(
                bindparam(
                    "vendor_pattern",
                    value=pattern
                )
            )
        )

    if currency:

        query = query.filter(
            Invoice.currency == currency
        )

    if start_date:

        start = parse_date(start_date)

        if start:

            query = query.filter(
                Invoice.invoice_date >= start
            )

    if end_date:

        end = parse_date(end_date)

        if end:

            query = query.filter(
                Invoice.invoice_date <= end
            )

    if min_amount is not None:

        query = query.filter(
            Invoice.total_amount >= min_amount
        )

    if max_amount is not None:

        query = query.filter(
            Invoice.total_amount <= max_amount
        )

    invoices = query.all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Invoice ID",
        "Invoice Number",
        "Vendor",
        "Vendor Normalized",
        "Invoice Date",
        "Amount",
        "Currency",
        "Review Status"
    ])

    for inv in invoices:

        writer.writerow([

            inv.id,

            inv.invoice_number,

            inv.vendor_name,

            inv.vendor_normalized,

            inv.invoice_date.strftime("%Y-%m-%d") if inv.invoice_date else "",

            inv.total_amount,

            inv.currency,

            inv.review_status

        ])

    output.seek(0)

    return StreamingResponse(

        iter([output.getvalue()]),

        media_type="text/csv",

        headers={

            "Content-Disposition":
            "attachment; filename=invoices.csv"

        }

    )



# ===========================
# REPORT
# ===========================

@app.get("/report")
def report():

    db = SessionLocal()

    total_documents = db.query(Document).count()

    total_invoices = db.query(Invoice).count()

    duplicates = len(duplicate_candidates())

    processed = (
        db.query(Document)
        .filter(Document.status == "processed")
        .count()
    )

    failed = (
        db.query(Document)
        .filter(Document.status == "failed")
        .count()
    )

    return {

        "documents": total_documents,

        "processed": processed,

        "failed": failed,

        "invoices": total_invoices,

        "possible_duplicates": duplicates

    }