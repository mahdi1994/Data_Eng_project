from src.scrapper import UrlScrapper
from urllib.parse import urlparse


class TourScrapperInfo(UrlScrapper):
    """

    """
    def __init__(self, url:str, table_class:str, table_stage_class:str, with_header: bool):
        super().__init__(url, table_class, with_header)
        self.table_stage_class = table_stage_class
        index = url.rfind('/')
        self.results_url = self.url[:index+1] + "results"
        parsed_url = urlparse(self.url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"



    def get_gc_selector_options(self):
        """
        get races information from /results
        :return:
        """

        soup = self.fetch_data()
        if self.table_stage_class == "pageSelectNav":
            dropdown_divs = soup.find_all("div", class_=self.table_stage_class)
            dropdown_div = soup.find_all("div", class_=self.table_stage_class)[len(dropdown_divs)-1] #pageSelectNav for /gc
        else:
            dropdown_div = soup.find("div", class_=self.table_stage_class)
        #soup = self.fetch_data()
        #dropdown_div = soup.find("div", class_="pageSelectNav 1") for étape d'un tour /results

        # Locate the <select> element inside the dropdown
        select_element = dropdown_div.find("select")

        # Extract all options from the select element
        options = select_element.find_all("option")

        stages = []

        for option in options:
            stage_url = option["value"]
            stage_name = option.text.strip()
            stages.append({"url": stage_url, "name": stage_name})

        return stages[:]

    def get_stages_selector(self):

        results_scrapper = UrlScrapper(self.results_url, "pageSelectNav 1", True)
        dropdown_div1 = results_scrapper.fetch_data().find("div", class_=results_scrapper.table_class)

        selection_element = dropdown_div1.find("select")

        stages_option = selection_element.find_all("option")

        stages_per_race = []

        for option in stages_option:
            stage_url = option["value"]
            stage_name = option.text.strip()
            stages_per_race.append({"url": f"{self.base_url}/{stage_url}", "name": stage_name})

        return stages_per_race[1:]

    def get_classification_tables(self):

        soup = self.fetch_data()
        nbr_stages = len(self.get_stages_selector())
        drop_down_gc = self.get_gc_selector_options()

        data_dict = {}
        tables = soup.find_all("table", {"class": f"{self.table_class}"})
        nbr_general_classifications = len(drop_down_gc) - nbr_stages

        for i in range(1, nbr_general_classifications+1):
            rows = tables[i].find("tbody").find_all("tr")
            if self.with_header:
                headers = tables[i].find("thead").find_all("th")
            else:
                headers = [""]

            # Initialize a key in the dictionary to hold all rows for this classification
            classification_name = drop_down_gc[nbr_stages - 1 + i]['name']
            if classification_name not in data_dict:
                data_dict[classification_name] = []
                print(classification_name)

            for index, row in enumerate(rows):

                columns = row.find_all("td")
                cells = [cell.text.strip() for cell in columns]
                headers_cell = [head.text.strip() for head in headers]

                # If headers are present, create a dictionary for each row using headers as keys
                if len(headers) == len(cells):
                    row_dict = {header: cells[i] for i, header in enumerate(headers_cell)}
                else:
                    # If no headers or mismatch, use numerical indices as keys
                    row_dict = {i: cells[i] for i in range(len(cells))}

                # Add the row dictionary to the main dictionary with the index as the key
                data_dict[classification_name].append(row_dict)

        return data_dict
