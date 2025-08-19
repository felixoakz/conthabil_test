import logging
import os
import re
from datetime import datetime

from conthabil.api_client import ApiClient
from conthabil.config import get_settings, setup_logging
from conthabil.scraper import Scraper
from conthabil.uploader import Uploader


def run_full_workflow():
    """
    Orchestrates the full workflow: scraping, uploading, and storing gazette data.
    """

    setup_logging()

    logging.info("Starting the full Conthabil workflow...")

    settings = get_settings()

    os.makedirs(settings.DOWNLOAD_PATH, exist_ok=True)


    # Step 1: Scrape files
    try:
        with Scraper(
            selenium_url=settings.SELENIUM_URL,
            download_path=settings.DOWNLOAD_PATH,
        ) as scraper:

            logging.info("Step 1: Starting scraping process...")
            downloaded_paths = scraper.find_and_download_files(target_url=settings.TARGET_URL)
            logging.info(f"Step 1: Scraping complete. Downloaded {len(downloaded_paths)} files.")

    except Exception as e:
        logging.critical(f"A critical error occurred during scraping: {e}")
        return

    if not downloaded_paths:
        logging.warning("No files downloaded. Skipping upload and storage steps.")
        return


    # Step 2: Upload files
    try:
        uploader = Uploader(upload_url=settings.UPLOAD_URL)

        logging.info("Step 2: Starting upload process...")
        uploaded_urls = uploader.upload_files(downloaded_paths)
        logging.info(f"Step 2: Upload complete. Uploaded {len(uploaded_urls)} files.")

    except Exception as e:
        logging.critical(f"A critical error occurred during uploading: {e}")
        return

    if not uploaded_urls:
        logging.warning("No files uploaded. Skipping storage step.")
        return


    # Step 3: Store URLs via API
    logging.info("Step 3: Storing uploaded URLs in the database via API...")

    api_client = ApiClient(base_url=settings.API_BASE_URL)

    upload_map = dict(zip(uploaded_urls, downloaded_paths))

    for uploaded_url, file_path in upload_map.items():
        filename = os.path.basename(file_path)
        try:
            match = re.search(r"(\d{8})", filename)
            if not match:
                raise ValueError("No YYYYMMDD date pattern found in filename")

            date_str = match.group(1)
            publication_date = datetime.strptime(date_str, "%Y%m%d")
            api_client.store_gazette(
                publication_date=publication_date, uploaded_url=uploaded_url
            )

        except (ValueError, IndexError) as e:
            logging.error(
                f"Error parsing date from filename '{filename}': {e}. "
                f"Skipping storage for {uploaded_url}."
            )

    logging.info("Full workflow completed.")


if __name__ == "__main__":
    run_full_workflow()
