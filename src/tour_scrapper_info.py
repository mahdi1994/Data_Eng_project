
from src.scrapper import UrlScrapper

class RaceScrapperInfo(UrlScrapper):
    """

    """
    def __init__(self, url:str, table_class:str, table_stage_class:str, with_header: bool):
        super().__init__(url, table_class, with_header)
        self.table_stage_class = table_stage_class

    def get_stages(self):

        soup = self.fetch_data()
        dropdown_div = soup.find("div", class_=self.table_stage_class)

        #soup = self.fetch_data()
        #dropdown_div = soup.find("div", class_="pageSelectNav 1")

        # Locate the <select> element inside the dropdown
        select_element = dropdown_div.find("select")

        # Extract all options from the select element
        options = select_element.find_all("option")

        stages = []

        for option in options:
            stage_url = option["value"]
            stage_name = option.text.strip()
            stages.append({"url": stage_url, "name": stage_name})

        return stages[1:]