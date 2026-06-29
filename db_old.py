from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///registry.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Association table (Many-to-Many)
invoice_documents = Table(
    "invoice_documents",
    Base.metadata,
    Column("invoice_id", Integer, ForeignKey("invoices.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    sha256 = Column(String, unique=True, nullable=False, index=True)

    size_bytes = Column(Integer)

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    status = Column(String, default="processed")

    failure_reason = Column(String)

    doc_type = Column(String, default="pdf")

    invoices = relationship(
        "Invoice",
        secondary=invoice_documents,
        back_populates="documents",
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(String)

    vendor_name = Column(String)

    vendor_normalized = Column(String)

    invoice_date = Column(DateTime)

    total_amount = Column(Float)

    currency = Column(String)

    review_status = Column(String, default="pending")

    deleted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship(
        "Document",
        secondary=invoice_documents,
        back_populates="invoices",
    )


def init_db():
    Base.metadata.create_all(bind=engine)
    return SessionLocal