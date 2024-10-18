import requests
from bs4 import BeautifulSoup


class RiderDataScraper:
    def __init__(self, url):
        self.url = url

    def fetch_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")

    def extract_rider_data(self, limit=20):
        soup = self.fetch_data()
        riders_table = soup.find('table', {'class': 'table table-striped'})
        rows = riders_table.find('tbody').find_all('tr')

        csv_data = "Rank,Name,Team,Country,Score\n"
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
            if count == limit:  # Limit to 'limit' entries
                break

        return csv_data
