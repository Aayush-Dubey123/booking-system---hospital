import os
import io
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from common.logger import logger

logging = logger(__name__)

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

if cloud_name and api_key and api_secret:
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


def upload_pdf_to_cloudinary(pdf_bytes: bytes, filename: str) -> str:
    """
    Uploads generated PDF bytes to Cloudinary as a raw PDF resource.
    No image transformations applied.
    """
    try:
        logging.info(f"Uploading PDF '{filename}' to Cloudinary")
        file_obj = io.BytesIO(pdf_bytes)
        # Use resource_type='raw' to upload raw PDF file without transformation
        result = cloudinary.uploader.upload(
            file_obj,
            resource_type="raw",
            public_id=f"prescriptions/{filename}",
            overwrite=True,
        )
        url = result.get("secure_url") or result.get("url")
        if not url:
            raise RuntimeError(f"Cloudinary response missing URL: {result}")
        logging.info(f"PDF uploaded successfully to Cloudinary: {url}")
        return url
    except Exception as error:
        logging.error(f"Error uploading PDF to Cloudinary: {error}")
        raise
