import os
from minio import Minio
from app.core.config import settings

class StorageManager:
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER.lower()
        if self.provider == "minio":
            try:
                self.client = Minio(
                    settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE
                )
                # Ensure bucket exists
                if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                    self.client.make_bucket(settings.MINIO_BUCKET_NAME)
            except Exception as e:
                # Fallback to local if MinIO connection fails
                print(f"Failed to initialize MinIO storage, falling back to Local. Error: {e}")
                self.provider = "local"
                self._ensure_local_dir()
        else:
            self._ensure_local_dir()

    def _ensure_local_dir(self):
        os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)

    def upload_file(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Uploads file content and returns a path/key string.
        """
        if self.provider == "minio":
            import io
            data_stream = io.BytesIO(content)
            self.client.put_object(
                settings.MINIO_BUCKET_NAME,
                filename,
                data_stream,
                length=len(content),
                content_type=content_type
            )
            return f"minio://{settings.MINIO_BUCKET_NAME}/{filename}"
        else:
            local_path = os.path.join(settings.LOCAL_STORAGE_DIR, filename)
            with open(local_path, "wb") as f:
                f.write(content)
            return local_path

    def download_file(self, file_key: str) -> bytes:
        """
        Downloads a file and returns its raw bytes.
        """
        if file_key.startswith("minio://"):
            parts = file_key.replace("minio://", "").split("/", 1)
            bucket = parts[0]
            object_name = parts[1]
            response = self.client.get_object(bucket, object_name)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        else:
            # Assume local filesystem path
            with open(file_key, "rb") as f:
                return f.read()

storage_manager = StorageManager()
