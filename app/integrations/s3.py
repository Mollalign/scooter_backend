"""S3-compatible object storage (DigitalOcean Spaces, MinIO, Cloudflare R2, AWS)."""

import logging
import uuid
from pathlib import PurePosixPath

import boto3
from botocore.config import Config

from app.core.config import settings

logger = logging.getLogger(__name__)


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY or None,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def generate_presigned_upload(
    *, prefix: str, content_type: str, expires_in: int = 600,
) -> dict:
    key = f"{prefix.strip('/')}/{uuid.uuid4().hex}"
    if "." in content_type:
        key += "." + content_type.split("/")[-1]
    url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )
    public_url = (
        f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"
        if settings.S3_PUBLIC_BASE_URL
        else url.split("?")[0]
    )
    return {"upload_url": url, "key": key, "public_url": public_url}


def object_public_url(key: str) -> str:
    if settings.S3_PUBLIC_BASE_URL:
        return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{PurePosixPath(key)}"
    return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET_NAME}/{key}"
