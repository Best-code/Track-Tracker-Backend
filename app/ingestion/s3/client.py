"""
AWS S3 client utilities for raw data storage.

This module provides helper functions for interacting with S3, including
uploading JSON data, listing bucket contents, and downloading files.

The S3 bucket is used to store raw API responses before processing,
enabling data replay and debugging.

Usage:
    from app.ingestion.s3.client import upload_json, download_json

    upload_json("my-bucket", "data/snapshot.json", {"key": "value"})
"""

import json
import logging
import os
from typing import Any

import boto3


logger = logging.getLogger(__name__)


def get_s3_client() -> boto3.client:
    """
    Create an S3 client with region from environment.

    Uses AWS_REGION environment variable, defaulting to us-east-1.
    Relies on standard AWS credential chain (env vars, ~/.aws/credentials, IAM role).

    Returns:
        boto3 S3 client instance
    """
    return boto3.client(
        "s3",
        region_name=os.environ.get("AWS_REGION", "us-east-1")
    )


def upload_json(bucket: str, key: str, data: dict[str, Any]) -> None:
    """
    Upload a dictionary as JSON to S3.

    Args:
        bucket: S3 bucket name
        key: Object key (path within bucket)
        data: Dictionary to serialize as JSON

    Raises:
        ClientError: If upload fails
    """
    s3 = get_s3_client()

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2, default=str),
        ContentType="application/json"
    )

    logger.info(f"Uploaded to s3://{bucket}/{key}")


def list_objects(bucket: str, prefix: str = "") -> list[dict[str, Any]]:
    """
    List objects in an S3 bucket with optional prefix filter.

    Args:
        bucket: S3 bucket name
        prefix: Key prefix to filter results (e.g., "raw/spotify/")

    Returns:
        List of object metadata dictionaries with keys like 'Key', 'Size', 'LastModified'
    """
    s3 = get_s3_client()

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return response.get("Contents", [])


def download_json(bucket: str, key: str) -> dict[str, Any]:
    """
    Download and parse a JSON file from S3.

    Args:
        bucket: S3 bucket name
        key: Object key to download

    Returns:
        Parsed JSON as dictionary

    Raises:
        ClientError: If download fails
        json.JSONDecodeError: If content is not valid JSON
    """
    s3 = get_s3_client()

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return json.loads(content)
