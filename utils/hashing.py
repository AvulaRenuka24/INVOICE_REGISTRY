import hashlib
from pathlib import Path


def sha256_file(file_path: str) -> str:
    """
    Compute SHA-256 hash of a file.
    Used for duplicate detection.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """
    Compute SHA-256 hash from uploaded file bytes.
    """

    return hashlib.sha256(data).hexdigest()


def file_size(file_path: str) -> int:
    """
    Return file size in bytes.
    """

    return Path(file_path).stat().st_size
