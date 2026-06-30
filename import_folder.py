import os
import requests

# Folder containing invoice PDFs
FOLDER = "data/sample_invoices"

# FastAPI Upload Endpoint
UPLOAD_URL = "http://127.0.0.1:8000/upload"

processed = 0
duplicates = 0
failed = 0

# Read every PDF in the folder
for filename in os.listdir(FOLDER):

    if not filename.lower().endswith(".pdf"):
        continue

    filepath = os.path.join(FOLDER, filename)

    print(f"\nUploading: {filename}")

    with open(filepath, "rb") as pdf:

        files = {
            "file": (
                filename,
                pdf,
                "application/pdf"
            )
        }

        response = requests.post(
            UPLOAD_URL,
            files=files
        )

    if response.status_code == 200:

        processed += 1

        print("✅ Uploaded Successfully")

        print(response.json())

    elif response.status_code == 409:

        duplicates += 1

        print("⚠ Duplicate File")

        print(response.json())

    else:

        failed += 1

        print("❌ Upload Failed")

        print(response.text)

print("\n===================================")
print("      IMPORT SUMMARY")
print("===================================")
print(f"Processed : {processed}")
print(f"Duplicates: {duplicates}")
print(f"Failed    : {failed}")
print("===================================")