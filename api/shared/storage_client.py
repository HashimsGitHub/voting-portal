"""
Storage Client
Helper for uploading candidate images to Azure Blob Storage
"""
import os
import uuid
import logging
from azure.storage.blob import BlobServiceClient, ContentSettings

logger = logging.getLogger(__name__)

CONTAINER_NAME = "candidates"


class StorageClient:
    """Thin wrapper around Azure Blob Storage for candidate image uploads"""

    def __init__(self, connection_string: str = None):
        connection_string = (
            connection_string
            or os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            or os.getenv('AzureWebJobsStorage')
        )
        if not connection_string:
            raise ValueError("Azure Storage connection string not configured")
        self.service_client = BlobServiceClient.from_connection_string(connection_string)
        self._ensure_container()

    def _ensure_container(self):
        try:
            self.service_client.create_container(CONTAINER_NAME)
        except Exception:
            # Container already exists
            pass

    def upload_image(self, file_bytes: bytes, content_type: str = "image/jpeg") -> str:
        """Upload image bytes and return the public blob URL"""
        extension = content_type.split('/')[-1] if '/' in content_type else 'jpg'
        blob_name = f"{uuid.uuid4()}.{extension}"
        container_client = self.service_client.get_container_client(CONTAINER_NAME)
        container_client.upload_blob(
            blob_name,
            file_bytes,
            content_settings=ContentSettings(content_type=content_type)
        )
        logger.info(f"Uploaded candidate image: {blob_name}")
        return container_client.get_blob_client(blob_name).url
