import logging
from datetime import datetime

import httpx


class ApiClient:
    """
    A client to handle communication with the gazette storage API.
    """

    def __init__(self, base_url: str):
        """
        Initializes the ApiClient.

        Args:
            base_url: The base URL of the API (e.g., 'http://app:8000/api').
        """

        self.base_url = base_url
        self.client = httpx.Client()


    def store_gazette(self, publication_date: datetime, uploaded_url: str) -> bool:
        """
        Posts a new gazette entry to the API.

        Args:
            publication_date: The publication date of the gazette.
            uploaded_url: The public URL of the file after uploading.

        Returns:
            True if the gazette was stored successfully, False otherwise.
        """

        endpoint = f"{self.base_url}/gazettes/"

        payload = {
            "url": uploaded_url,
            "publication_date": publication_date.isoformat(),
        }

        try:
            response = self.client.post(endpoint, json=payload)
            response.raise_for_status()
            return True

        except httpx.HTTPStatusError as e:
            logging.error(
                f"Error storing URL {uploaded_url} via API: {e}. "
                f"Response: {e.response.text}"
            )
            return False

        except httpx.RequestError as e:
            logging.error(f"Error storing URL {uploaded_url} via API: {e}")
            return False

