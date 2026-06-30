# Invoice Registry

A FastAPI-based Invoice Registry application developed as part of an AI/ML internship assignment. The application allows users to upload invoice PDFs, automatically extract invoice information, detect duplicate files and invoices, search invoices, review duplicate candidates, and export invoice data.

---

#  Features

-  Upload Invoice PDF
-  Extract Invoice Details
-  SHA-256 Duplicate File Detection
-  Exact Duplicate Invoice Detection
-  Near Duplicate Detection using RapidFuzz
-  Search Invoices
-  Filter by Vendor, Date, Amount and Currency
-  Soft Delete Invoices
-  Duplicate Review Workflow
-  Dashboard Statistics
-  CSV Export
-  Logging
-  Unit Testing

---

# 🛠 Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

## Frontend

- HTML
- CSS
- JavaScript
- Jinja2 Templates

## Libraries

- pdfplumber
- RapidFuzz
- python-dateutil
- python-multipart
- requests

## Tools

- Git
- GitHub
- VS Code

---

# 📂 Project Structure

```
INVOICE_REGISTRY
│
├── api.py
├── db.py
├── extractor.py
├── fuzzy.py
├── config.yaml
├── requirements.txt
├── import_folder.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── utils/
│   ├── cleaning.py
│   ├── hashing.py
│   └── logging_config.py
│
├── tests/
│   └── test_dedup.py
│
├── uploads/
├── reports/
└── data/
```

---

# 🗄 Database Schema

The application uses **SQLite** with **SQLAlchemy ORM**.

## 1. Documents

Stores metadata about uploaded PDF files.

| Field | Description |
|--------|-------------|
| id | Primary Key |
| filename | PDF filename |
| size_bytes | File size |
| sha256 | SHA-256 hash |
| status | processed / failed |
| failure_reason | Failure description |
| doc_type | PDF |
| uploaded_at | Upload timestamp |

---

## 2. Invoices

Stores extracted invoice information.

| Field | Description |
|--------|-------------|
| id | Primary Key |
| invoice_number | Invoice Number |
| vendor_name | Vendor Name |
| vendor_normalized | Normalized Vendor |
| invoice_date | Invoice Date |
| total_amount | Invoice Amount |
| currency | Currency |
| review_status | Review Status |
| deleted_at | Soft Delete Timestamp |
| created_at | Record Creation Time |

---

## 3. Invoice Documents

Many-to-many relationship between invoices and uploaded documents.

| Field |
|--------|
| invoice_id |
| document_id |

---

## 4. Duplicate Candidates

Stores possible duplicate invoices for manual review.

| Field |
|--------|
| id |
| invoice1_id |
| invoice2_id |
| vendor_score |
| invoice_score |
| status |

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/AvulaRenuka24/INVOICE_REGISTRY.git
```

Move into the project

```bash
cd IN