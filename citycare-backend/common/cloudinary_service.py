import os
import io
from pathlib import Path

from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# pyrefly: ignore [missing-import]
from common.logger import logger


logging = logger(__name__)

# Project-root .env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

if not cloud_name or not api_key or not api_secret:
    raise RuntimeError("Cloudinary credentials are missing from .env")

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True,
)


def upload_pdf_to_cloudinary(pdf_bytes: bytes, filename: str) -> str:
    """
    Upload a PDF to Cloudinary as a raw resource and return
    a signed HTTPS delivery URL.
    """

    try:
        logging.info(f"Uploading PDF '{filename}' to Cloudinary")

        # Ensure we are uploading actual PDF bytes.
        if not pdf_bytes:
            raise ValueError("PDF bytes are empty")

        if not pdf_bytes.startswith(b"%PDF"):
            raise ValueError("Invalid PDF data: file does not start with %PDF")

        file_obj = io.BytesIO(pdf_bytes)

        public_id = f"prescriptions/{filename}"

        result = cloudinary.uploader.upload(
            file_obj,
            resource_type="raw",
            type="upload",
            public_id=public_id,
            overwrite=True,
            invalidate=True,
        )

        actual_public_id = result["public_id"]
        version = result.get("version")

        # Generate a signed HTTPS Cloudinary delivery URL.
        pdf_url, _ = cloudinary_url(
            actual_public_id,
            resource_type="raw",
            type="upload",
            version=version,
            secure=True,
            sign_url=True,
        )

        if not pdf_url:
            raise RuntimeError(
                f"Cloudinary did not return a valid delivery URL: {result}"
            )

        logging.info(
            f"PDF uploaded successfully to Cloudinary: {pdf_url}"
        )

        return pdf_url

    except Exception as error:
        logging.error(
            f"Error uploading PDF to Cloudinary: {error}"
        )
        raise