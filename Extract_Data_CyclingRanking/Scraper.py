import requests
from bs4 import BeautifulSoup


class CyclingDataScraper:
    def __init__(self, url, table_class):
        """
        Initializes the scrapper with the URL and the class of the table to extract.
        :param url: URL of the page to scrape.
        :param table_class: Class name of the table to extract data from.
        """
        self.url = url
        self.table_class = table_class

    def fetch_data(self):
        """
        Fetch the page content from the URL.
        :return: BeautifulSoup object of the page content.
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")

    def extract_data(self, with_headers):
        soup = self.fetch_data()
        table = soup.find('table', {'class': f'{self.table_class}'})
        rows = table.find('tbody').find_all('tr')
        if with_headers:
            headers = [header.text.strip() for header in table.find('thead').find_all('th')]
        else:
            headers = ['']

        return rows, headers


    def process_ranking_rows(self, with_headers, limit=20):
        """
        Processes the table rows and formats them into a CSV string.
        :param with_headers:
        :param rows: List of table rows (tr elements) to process.
        :param limit: The maximum number of rows to process.
        :return: A CSV-formatted string.
        """
        rows, headers = self.extract_data(with_headers)
        csv_data = ','.join(headers) + '\n'
        count = 0

        for row in rows:
            columns = row.find_all('td')
            rank = columns[0].text.strip().split('.')[0]
            name = columns[1].text.strip().split('\n')[0]
            team = columns[2].text.strip()
            country = columns[3].text.strip()
            score = columns[4].text.strip()
            csv_data += f"{rank},{name},{team},{country},{score}\n"

            count += 1
            if count == limit:
                break

        return csv_data

