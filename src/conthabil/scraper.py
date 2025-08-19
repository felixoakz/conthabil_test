import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from types import TracebackType
from typing import Self

import httpx
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class Scraper:
    """
    A class to handle the scraping of documents from the specified URL.
    It connects to a remote Selenium WebDriver and is designed to be used as a context manager.
    """

    def __init__(self, selenium_url: str, download_path: str):
        """
        Initializes the Scraper.

        Args:
            selenium_url: The URL of the remote Selenium WebDriver.
            download_path: The directory to save downloaded files.
        """

        self.selenium_url = selenium_url
        self.download_path = download_path
        self.driver: WebDriver | None = None


    def __enter__(self) -> Self:
        """
        Enters the context manager, setting up the WebDriver session.
        """
        self.driver = self._setup_driver()
        return self


    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exits the context manager, closing the WebDriver session.
        """

        if self.driver:
            logging.debug("Closing WebDriver session.")
            self.driver.quit()


    def _setup_driver(self) -> WebDriver:
        """
        Sets up the remote Selenium Chrome WebDriver.

        Returns:
            An instance of the remote Selenium WebDriver.
        """

        logging.debug(f"Connecting to remote WebDriver at {self.selenium_url}")
        chrome_options = Options()

        try:
            driver = webdriver.Remote(
                command_executor=self.selenium_url, options=chrome_options
            )
            logging.debug("Successfully connected to remote WebDriver.")
            return driver

        except Exception as e:
            logging.error(f"Failed to connect to remote WebDriver: {e}")
            raise


    def find_and_download_files(self, target_url: str) -> list[str]:
        """
        Finds and downloads all relevant PDF files from the target URL for the
        previous month.

        Args:
            target_url: The URL to scrape.

        Returns:
            A list of local file paths for the downloaded files.
        """

        if not self.driver:
            raise RuntimeError("WebDriver not initialized. Use the 'with' statement.")

        logging.debug(f"Navigating to {target_url}")
        self.driver.get(target_url)

        self._perform_search()
        self._set_pagination()

        pdf_links = self._find_pdf_links()
        downloaded_files = self._download_all_files(pdf_links)

        return downloaded_files


    def _perform_search(self) -> None:
        """Calculates the previous month and performs the search."""

        assert self.driver, "WebDriver is not initialized."

        today = datetime.today()
        previous_month_date = today - relativedelta(months=1)
        target_month = previous_month_date.strftime("%m")
        target_year = previous_month_date.strftime("%Y")

        logging.info(f"Performing search for month/year: {target_month}/{target_year}")

        try:
            month_select = Select(self.driver.find_element(By.NAME, "mes"))
            month_select.select_by_value(target_month)

            year_select = Select(self.driver.find_element(By.NAME, "ano"))
            year_select.select_by_value(target_year)

            search_button = self.driver.find_element(
                By.CSS_SELECTOR, "form[data-request='onTest'] button[type='submit']"
            )
            search_button.click()

            wait = WebDriverWait(self.driver, 15)
            expected_text_in_link = f"/{target_month}/{target_year}"
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//a[contains(text(), '{expected_text_in_link}')]")
                )
            )
            logging.info("Search successful and results loaded.")

        except Exception as e:
            logging.error(f"An error occurred during form interaction: {e}")
            raise


    def _set_pagination(self) -> None:
        """Sets the result pagination to show 100 entries per page."""

        assert self.driver, "WebDriver is not initialized."

        try:
            logging.debug("Changing pagination to show 100 results per page.")
            pagination_select = Select(
                self.driver.find_element(By.NAME, "example_length")
            )
            pagination_select.select_by_value("100")
            logging.debug("Successfully set pagination to 100.")

            wait = WebDriverWait(self.driver, 10)
            wait.until(
                lambda d: len(
                    d.find_elements(By.XPATH, "//table[@id='example']/tbody/tr")
                )
                > 10
            )
            logging.debug("Table successfully reloaded with more entries.")

        except Exception:
            logging.warning(
                "Could not change pagination to 100. "
                "This may happen with few results."
            )


    def _find_pdf_links(self) -> list[str]:
        """
        Finds all PDF links within the results table.

        Returns:
            A list of strings, where each string is a URL to a PDF file.
        """

        assert self.driver, "WebDriver is not initialized."

        logging.debug("Finding all PDF links on the page...")
        link_elements = self.driver.find_elements(
            By.XPATH, "//table[@id='example']/tbody/tr/td/a"
        )
        pdf_links = [
            href
            for elem in link_elements
            if (href := elem.get_attribute("href"))
        ]
        logging.info(f"Found {len(pdf_links)} PDF links.")
        return pdf_links


    def _download_all_files(self, links: list[str]) -> list[str]:
        """
        Downloads all files from a list of links concurrently.

        Args:
            links: A list of URLs to download.

        Returns:
            A list of local paths for the successfully downloaded files.
        """

        logging.info(f"Starting concurrent download of {len(links)} files...")

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(self._download_file, links))

        downloaded_files = [path for path in results if path is not None]
        logging.info(
            f"Finished downloading. {len(downloaded_files)} files saved."
        )
        return downloaded_files


    def _download_file(self, link: str) -> str | None:
        """
        Downloads a single file from a given link using httpx.

        Args:
            link: The URL of the file to download.

        Returns:
            The local path of the downloaded file, or None if download fails.
        """

        try:
            filename = os.path.basename(link)
            save_path = os.path.join(self.download_path, filename)

            with httpx.stream("GET", link, follow_redirects=True) as response:
                response.raise_for_status()
                with open(save_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            return save_path

        except httpx.RequestError as e:
            logging.error(f"Error downloading {link}: {e}")
            return None

