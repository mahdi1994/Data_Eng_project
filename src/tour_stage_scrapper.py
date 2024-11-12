from src.one_day_race_scrapper import OneDayRaceScrapper
from src.tour_scrapper_info import TourScrapperInfo
from bs4 import BeautifulSoup
import requests

class TourStageScrapper(OneDayRaceScrapper):
    """


    """
    def __init__(self, url: str, table_class: str, ul_class: str, with_header: bool):
        super().__init__(url, table_class, ul_class, with_header)
        index = self.url.rfind("/")
        self.results_url = self.url[:index+1] + "results"

        self.ul_class = ul_class
        self.soup = self.fetch_data()

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

            #rows_list = []
            #headers_list = []

            tables = soup.find_all("table", {"class": f"{self.table_class}"})
            rows = tables[0].find("tbody").find_all("tr")
            if self.with_header:
                # headers = [
                #     header.text.strip() for header in tables[0].find("thead").find_all("th")
                # ]
                headers =  tables[0].find("thead").find_all("th")
            else:
                headers = [""]
            #rows_list.append(rows)
            #headers_list.append(headers)

            return rows, headers

    def process_race_info(self):

        soup = self.soup

        element = soup.find("ul", {"class": f"{self.ul_class}"})

        race_info_list = []

        lines = element.find_all('li')
        cells = [cell.text.strip() for cell in lines]

        race_info = {}
        for cell in cells:
            if ':' in cell:
                key, value = cell.split(':', 1)
                race_info[key.strip()] = value.strip()

        #getting the parcours type
        for div in lines:
            content = div.find('span')
            if content is not None:
                race_info['Parcours type'] = content['class'][-1]

        race_info_list.append(race_info)
        return race_info_list

    def process_rows(self) -> dict:
        """
        Processes the table rows and converts them into a dictionary.

        Args:
            with_header (bool): A flag to indicate if the table headers should be included
                                in the dictionary. If True, the headers are extracted.

        Returns:
            dict: A dictionary representing the table rows. Each key is an index, and the value
                  is a dictionary containing the row data with headers as keys (if available)
                  or indices (if not).
        """
        # Extract the rows and headers using your existing method
        rows, header = self.extract_table()
        data_dict = []

        # Loop through each row in the table

        for index, row in enumerate(rows):
            # Find all 'td' elements (table data cells) in the current row
            columns = row.find_all("td")
            # Extract and clean text from each cell
            cells = [cell.text.strip() for cell in columns]
            headers = [head.text.strip() for head in header]

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
                Merges race information and rows data, then returns it as a JSON string.

                Returns:
                    str: A JSON string representing the merged race information and rows data.
                """
        race_info = self.process_race_info()  # Get race info list
        rows_data = self.process_rows()  # Get rows data list

        # Merging the data
        merged_data = {
            "race_info": race_info,
            "rows_data": rows_data
        }

        # Return the merged data as a JSON string
        return merged_data  # Use indent for pretty printing

    def get_stages(self) -> tuple:
        """
        get stages list and number for a race
        :return:
        """

        #instantiate a TourScrapperInfo
        race_stages = TourScrapperInfo(self.results_url, "", "pageSelectNav 1", True)
        stages = race_stages.get_infos()
        nbr_stages = len(stages)
        return stages, nbr_stages


