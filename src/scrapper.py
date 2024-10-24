# pylint: disable = missing-module-docstring)
import requests
from bs4 import BeautifulSoup
import pandas as pd


class UrlScrapper:
    """
    Initializes the UrlScrapper with the URL and the table class to scrape

    Args:
        url (str): The URL of the page to scrape.
        table_class (str): The CSS class of the table to extract data from.
    """

    def __init__(self, url : str, table_class :str, with_header: bool):
        self.url = url
        self.table_class = table_class
        self.with_header = with_header

    def fetch_data(self) -> BeautifulSoup:
        """
        Fetch the page content from the URL.
        return: BeautifulSoup object of the page content.
        """
        response = requests.get(self.url, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")

        raise requests.exceptions.HTTPError(
            f"Failed to retrieve data. Status code: {response.status_code}"
        )

    def extract_table(self) -> tuple:
        """
        Extracts data from the table found on the web page.

        Args:

            with_headers (bool): A flag to specify whether to extract table headers
            or not. If True, headers will be extracted.

        Returns:
            tuple:
                - rows (list): A list of BeautifulSoup table row 'tr' elements representing
                  the rows of the table.
                - headers (list): A list of strings representing the column headers
                  if `with_headers` is True, or an empty string if False.
        """
        soup = self.fetch_data()

        table = soup.find("table", {"class": f"{self.table_class}"})
        rows = table.find("tbody").find_all("tr")
        if self.with_header:
            headers = [
                header.text.strip() for header in table.find("thead").find_all("th")
            ]
        else:
            headers = [""]

        return rows, headers

    def process_rows(self) -> pd.DataFrame:
        """
        Processes the table rows and converts them into a pandas DataFrame.

        Args:
            with_header (bool): A flag to indicate if the table headers should be included
                                in the DataFrame. If True, the headers are extracted.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the extracted table data.
                          If `with_header` is True, the DataFrame will have column
                          headers; otherwise, it will not.
        """
        rows, headers = self.extract_table()
        data = []
        # Loop through each row in the table
        for row in rows:
            # Find all 'td' elements (table data cells) in the current row
            columns = row.find_all("td")
            # Extract and clean text from each cell, and store it in a list
            cells = [cell.text.strip() for cell in columns]
            data.append(cells)

        if len(headers) != len(data[0]):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=headers)
        return df
