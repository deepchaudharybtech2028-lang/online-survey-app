
import os
from google.cloud import storage


def upload_file(file_path, destination_name):
    bucket_name = os.getenv("GCS_BUCKET")

    # Keep local mode working without Google Cloud
    if not bucket_name:
        print("Google Cloud Storage is not configured.")
        return None

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_name)

    blob.upload_from_filename(file_path)

    return f"Uploaded {destination_name}"
