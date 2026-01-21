"""S3/MinIO object storage client and helpers."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aioboto3
from botocore.config import Config

from src.core.config import settings


def get_s3_config() -> dict:
    """Get S3 client configuration."""
    return {
        "endpoint_url": settings.s3_endpoint_url,
        "aws_access_key_id": settings.s3_access_key,
        "aws_secret_access_key": settings.s3_secret_key,
        "region_name": settings.s3_region,
        "config": Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    }


@asynccontextmanager
async def get_s3_client() -> AsyncGenerator:
    """Get async S3 client context manager.

    Usage:
        async with get_s3_client() as client:
            await client.upload_fileobj(...)
    """
    session = aioboto3.Session()
    async with session.client("s3", **get_s3_config()) as client:
        yield client


def generate_storage_key(
    assessment_id: uuid.UUID,
    question_id: uuid.UUID,
    original_filename: str,
) -> str:
    """Generate a unique storage key for an attachment.

    Args:
        assessment_id: The assessment UUID.
        question_id: The question UUID.
        original_filename: Original filename for extension.

    Returns:
        Storage key in format: assessments/{assessment_id}/{question_id}/{uuid}.{ext}
    """
    # Extract file extension
    ext = ""
    if "." in original_filename:
        ext = original_filename.rsplit(".", 1)[-1].lower()

    # Generate unique filename
    unique_id = uuid.uuid4()
    filename = f"{unique_id}.{ext}" if ext else str(unique_id)

    return f"assessments/{assessment_id}/{question_id}/{filename}"


async def upload_file(
    file_content: bytes,
    storage_key: str,
    content_type: str,
) -> str:
    """Upload a file to S3/MinIO.

    Args:
        file_content: The file bytes to upload.
        storage_key: The S3 object key.
        content_type: MIME type of the file.

    Returns:
        The storage key of the uploaded file.
    """
    async with get_s3_client() as client:
        await client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=storage_key,
            Body=file_content,
            ContentType=content_type,
        )
    return storage_key


async def delete_file(storage_key: str) -> None:
    """Delete a file from S3/MinIO.

    Args:
        storage_key: The S3 object key to delete.
    """
    async with get_s3_client() as client:
        await client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=storage_key,
        )


async def get_presigned_url(storage_key: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for downloading a file.

    Args:
        storage_key: The S3 object key.
        expires_in: URL expiration in seconds (default 1 hour).

    Returns:
        Presigned URL for the object.
    """
    async with get_s3_client() as client:
        url = await client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.s3_bucket_name,
                "Key": storage_key,
            },
            ExpiresIn=expires_in,
        )
    return url


async def ensure_bucket_exists() -> None:
    """Ensure the configured bucket exists, creating it if necessary."""
    async with get_s3_client() as client:
        try:
            await client.head_bucket(Bucket=settings.s3_bucket_name)
        except client.exceptions.ClientError:
            await client.create_bucket(Bucket=settings.s3_bucket_name)
