from src.scrapper import UrlScrapper
import json
class OneDayRaceScrapper(UrlScrapper):
    """


    """
    def __init__(self, url: str, table_class: str, ul_class: str, with_header: bool):
        super().__init__(url, table_class, with_header)
        self.ul_class = ul_class
        self.soup = self.fetch_data()

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
        rows, headers = self.extract_table()
        data_dict = []

        # Loop through each row in the table
        for index, row in enumerate(rows):
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


    def stage_process(self) -> str:
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
        return json.dumps(merged_data, indent=4)  # Use indent for pretty printing