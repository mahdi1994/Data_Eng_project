# pylint: disable = missing-module-docstring)
from urllib.parse import urlparse
import pandas as pd
from scrapper import UrlScrapper


class RacesScrapper(UrlScrapper):
    """
    Initializes the RaceScrapper with the URL and the table class to scrape

    Args:
        url (str): The URL of the page to scrape.
        table_class (str): The CSS class of the table to extract data from.
        with_header (bool): to get the header dynamically
    """

    def __init__(self, url: str, table_class: str, with_header: bool):
        super().__init__(url, table_class, with_header)
        parsed_url = urlparse(self.url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"

    def process_rows(self) -> tuple:
        """
        Processes the table rows to extract race data and corresponding URLs dynamically.

        Returns:
            tuple: A tuple containing two DataFrames:
                - df_data: DataFrame with the race data extracted from the table.
                - df_link: DataFrame with the date and the dynamic race URL for each row.

        """
        # Extract rows and headers from the table
        rows, headers = self.extract_table()
        link_data = []
        race_data = []

        for row in rows:
            # Find all columns (td elements) in the row
            columns = row.find_all("td")
            # Extract the text content of each cell in the row
            cells = [cell.text.strip() for cell in columns]
            race_url = None

            # Dynamically find the column that contains the link (an <a> tag with href attribute)
            for column in columns:
                link = column.find("a", href=True)
                if link:
                    # Use base_url extracted in the constructor to construct the full URL
                    race_url = f"{self.base_url}{link['href']}"
                    break  # Exit the loop once the link is found

            # Assume the first column contains the date
            date = columns[0].text.strip()
            race_name = columns[2].text.strip()
            # Store the date and race URL in link_data
            link_data.append([date, race_name, race_url])
            # Store the full row data in race_data
            race_data.append(cells)

        # Create DataFrame for race data and link data
        df_data = pd.DataFrame(race_data, columns=headers)
        df_link = pd.DataFrame(link_data, columns=["Date", "Race_Name", "Link"])
        df_link["Is_one_day_race"] = df_link["Date"].apply(lambda x: x.find("-") == -1)

        return df_data, df_link
