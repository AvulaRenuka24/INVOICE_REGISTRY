from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    Table,
)

from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
)

DATABASE_URL = "sqlite:///registry.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


invoice_documents = Table(
    "invoice_documents",
    Base.metadata,
    Column(
        "invoice_id",
        Integer,
        ForeignKey("invoices.id"),
        primary_key=True,
    ),
    Column(
        "document_id",
        Integer,
        ForeignKey("documents.id"),
        primary_key=True,
    ),
)


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    filename = Column(String, nullable=False)

    size_bytes = Column(Integer)

    sha256 = Column(
        String,
        unique=True,
        index=True,
    )

    status = Column(String)

    failure_reason = Column(String)

    doc_type = Column(String)

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    invoices = relationship(
        "Invoice",
        secondary=invoice_documents,
        back_populates="documents",
    )


class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)

    invoice_number = Column(String)

    vendor_name = Column(String)

    vendor_normalized = Column(
        String,
        index=True,
    )

    invoice_date = Column(DateTime)

    total_amount = Column(Numeric(12, 2))

    currency = Column(String)

    review_status = Column(
        String,
        default="unreviewed",
    )

    deleted_at = Column(DateTime)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    documents = relationship(
        "Document",
        secondary=invoice_documents,
        back_populates="invoices",
    )


class DuplicateCandidate(Base):

    __tablename__ = "duplicate_candidates"

    id = Column(Integer, primary_key=True)

    invoice1_id = Column(
        Integer,
        ForeignKey("invoices.id"),
    )

    invoice2_id = Column(
        Integer,
        ForeignKey("invoices.id"),
    )

    vendor_score = Column(Integer)

    invoice_score = Column(Integer)

    status = Column(
        String,
        default="pending",
    )


def init_db():

    Base.metadata.create_all(bind=engine)