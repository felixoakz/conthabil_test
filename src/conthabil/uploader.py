import logging
import os
from concurrent.futures import ThreadPoolExecutor

import httpx


class Uploader:
    """
    Handles uploading files to a specified URL.
    """

    def __init__(self, upload_url: str):
        """
        Initializes the Uploader.

        Args:
            upload_url: The target URL for file uploads.
        """
        self.upload_url = upload_url


    def upload_files(self, file_paths: list[str]) -> list[str]:
        """
        Uploads a list of files concurrently.

        Args:
            file_paths: A list of local file paths to upload.

        Returns:
            A list of public URLs for the uploaded files.
        """

        logging.info(f"Starting concurrent upload of {len(file_paths)} files...")

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self._upload_file, file_paths))

        uploaded_urls = [url for url in results if url is not None]

        logging.info(f"Finished uploading. {len(uploaded_urls)} files uploaded.")

        return uploaded_urls


    def _upload_file(self, file_path: str) -> str | None:
        """
        Uploads a single file using a multipart/form-data POST request.

        Args:
            file_path: The local path of the file to upload.

        Returns:
            The public URL of the uploaded file, or None if the upload fails.
        """

        try:
            file_name = os.path.basename(file_path)

            with open(file_path, "rb") as f:
                files = {"file": (file_name, f, "application/pdf")}

                with httpx.Client() as client:
                    response = client.post(self.upload_url, files=files)
                    response.raise_for_status()

            url = response.text.strip()

            return url

        except (httpx.RequestError, IOError) as e:
            logging.error(f"Error uploading {file_path}: {e}")
            return None

