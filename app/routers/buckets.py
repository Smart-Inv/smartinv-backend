from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from google.cloud import storage
from datetime import datetime

router = APIRouter()
BUCKET_NAME = "smartinv"

def upload_file_to_bucket(file: UploadFile, destination_blob_name: str):
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(file.file, content_type=file.content_type)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file to bucket: {e}")

@router.post("/upload_csv/", tags=["model"], status_code=status.HTTP_201_CREATED)
async def upload_csv(name_company: str = Form(...), csv_file: UploadFile = File(...)):
    if not csv_file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    destination_name = f"{name_company.lower()}/dataset_{timestamp}.csv"

    upload_file_to_bucket(csv_file, destination_name)

    return {
        "message": "CSV uploaded successfully",
        "bucket": BUCKET_NAME,
        "file_path": destination_name
    }
