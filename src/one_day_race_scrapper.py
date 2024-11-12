"""
Module for scraping one-day cycling race data.

This module defines the `OneDayRaceScrapper` class, which extends `UrlScrapper` to scrape
race information and race results from one-day cycling race pages.
"""

from src.scrapper import UrlScrapper




class OneDayRaceScrapper(UrlScrapper):
    """
    A scraper for one-day cycling race data.

    Inherits from UrlScrapper and adds methods specific to extracting detailed information
    about one-day races, including race-specific metadata and race results.
    """

    def __init__(self, url: str, table_class: str, ul_class: str, with_header: bool):
        """
        Initializes the OneDayRaceScrapper with a URL and HTML class names for the table and list.

        Args:
            url (str): The URL of the one-day race page to scrape.
            table_class (str): The HTML class of the race results table.
            ul_class (str): The HTML class of the unordered list containing race metadata.
            with_header (bool): A flag indicating if the table has headers.
        """
        super().__init__(url, table_class, with_header)
        self.ul_class = ul_class
        self.soup = self.fetch_data()

    def process_race_info(self):
        """
        Processes race information metadata from the unordered list on the page.

        Returns:
            list: A list containing a dictionary with race metadata.
        """

        soup = self.soup

        element = soup.find("ul", {"class": f"{self.ul_class}"})

        race_info_list = []

        lines = element.find_all("li")
        cells = [cell.text.strip() for cell in lines]

        race_info = {}
        for cell in cells:
            if ":" in cell:
                key, value = cell.split(":", 1)
                race_info[key.strip()] = value.strip()

        # getting the parcours type
        for div in lines:
            content = div.find("span")
            if content is not None:
                race_info["Parcours type"] = content["class"][-1]

        race_info_list.append(race_info)
        return race_info_list

    def process_rows(self) -> list:
        """
        Processes the table rows and converts them into a list of dictionaries.

        Returns:
            list: A list of dictionaries where each dictionary represents a row in the table.
        """
        # Extract the rows and headers using your existing method
        rows, headers = self.extract_table()
        data_dict = []

        # Loop through each row in the table
        for row in rows:
            # Find all 'td' elements (table data cells) in the current row
            columns = row.find_all("td")
            # Extract and clean text from each cell
            cells = [cell.text.strip() for cell in columns]

            # If headers are present, create a dictionary for each row using headers as keys
            if len(headers) == len(cells):
                row_dict = {header: cells[i] for i, header in enumerate(headers)}
            else:
                # If no headers or mismatch, use numerical indices as keys
                row_dict = {i: cells[i] for i in range(len(cells))}

            # Add the row dictionary to the main dictionary with the index as the key
            data_dict.append(row_dict)

        return data_dict

    def stage_process(self) -> dict:
        """
        Merges race information and rows data, then returns it as a dictionary.

        Returns:
            dict: A dictionary with race metadata and results.
        """
        race_info = self.process_race_info()  # Get race info list
        rows_data = self.process_rows()  # Get rows data list

        # Merging the data
        merged_data = {"race_info": race_info, "rows_data": rows_data}

        # Return the merged data as a JSON string
        return merged_data  # Use indent for pretty printing
