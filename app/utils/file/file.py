import mimetypes
import os
import uuid
from pathlib import PurePosixPath
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


def _normalize_relative_path(path):
    path = str(path).replace("\\", "/")
    parsed_path = urlparse(path)

    if parsed_path.scheme or parsed_path.netloc or path.startswith("/"):
        raise ValueError("The upload path must be relative")

    relative_path = PurePosixPath(path)
    if ".." in relative_path.parts:
        raise ValueError("The upload path must be relative")

    normalized_path = str(relative_path)
    if normalized_path in ("", "."):
        raise ValueError("The upload path must not be empty")

    return normalized_path


def _get_bucket_settings():
    bucket_endpoint = os.getenv("DIGITALOCEAN_SPACES_BUCKET_ENDPOINT")
    if not bucket_endpoint:
        raise ValueError("DIGITALOCEAN_SPACES_BUCKET_ENDPOINT is not configured")

    parsed_endpoint = urlparse(bucket_endpoint)
    host_parts = parsed_endpoint.netloc.split(".")

    if len(host_parts) < 2:
        raise ValueError("DIGITALOCEAN_SPACES_BUCKET_ENDPOINT is not valid")

    bucket_name = host_parts[0]
    region_name = host_parts[1]
    endpoint_url = f"https://{region_name}.digitaloceanspaces.com"
    base_prefix = parsed_endpoint.path.strip("/")

    return {
        "base_url": bucket_endpoint.rstrip("/"),
        "base_prefix": base_prefix,
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "region_name": region_name,
    }


def _get_spaces_client(settings):
    access_key = os.getenv("DIGITALOCEAN_SPACES_API_KEY")
    secret_key = os.getenv("DIGITALOCEAN_SPACES_SECRET_KEY")

    client_config = {
        "service_name": "s3",
        "region_name": settings["region_name"],
        "endpoint_url": settings["endpoint_url"],
        "config": Config(signature_version="s3v4"),
    }

    if access_key and secret_key:
        client_config.update(
            {
                "aws_access_key_id": access_key,
                "aws_secret_access_key": secret_key,
            }
        )

    return boto3.client(**client_config)


def _get_fileobj(file):
    return getattr(file, "file", file)


def _get_content_type(file, path):
    content_type = getattr(file, "content_type", None)
    if content_type:
        return content_type

    guessed_type, _ = mimetypes.guess_type(path)
    return guessed_type


def _build_storage_key(settings, relative_path):
    if settings["base_prefix"]:
        return f"{settings['base_prefix']}/{relative_path}"

    return relative_path


def _add_unique_id_to_filename(filename, relative_path):
    return f"{relative_path}/{uuid.uuid4()}-{filename}"


def upload_file(file, path):
    settings = _get_bucket_settings()    
    relative_path = _normalize_relative_path(path)
    unique_relative_path = _add_unique_id_to_filename(file.filename, relative_path)
    storage_key = _build_storage_key(settings, unique_relative_path)
    client = _get_spaces_client(settings)

    fileobj = _get_fileobj(file)
    if hasattr(fileobj, "seek"):
        fileobj.seek(0)

    extra_args = {"ACL": "public-read"}
    content_type = _get_content_type(file, unique_relative_path)
    if content_type:
        extra_args["ContentType"] = content_type

    client.upload_fileobj(
        fileobj,
        settings["bucket_name"] ,
        storage_key,
        ExtraArgs=extra_args,
    )

    return f"{settings['base_url']}/{unique_relative_path}"
