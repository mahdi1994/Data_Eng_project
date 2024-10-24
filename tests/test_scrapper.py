import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
from src.scrapper import UrlScrapper, pd # Replace 'your_module' with the actual module name


class TestUrlScrapper(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_data_success(self, mock_get):
        # Mock the response of requests.get
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = '<html><body><table class="test"><tr><td>Data</td></tr></table></body></html>'

        scrapper = UrlScrapper("http://example.com", "test", True)
        soup = scrapper.fetch_data()

        self.assertIsInstance(soup, BeautifulSoup)

    @patch('requests.get')
    def test_fetch_data_failure(self, mock_get):
        # Mock a failed response
        mock_get.return_value.status_code = 404

        scrapper = UrlScrapper("http://example.com", "test", True)

        with self.assertRaises(Exception) as context:
            scrapper.fetch_data()

        self.assertEqual(str(context.exception), "Failed to retrieve data. Status code: 404")

    @patch('requests.get')
    def test_extract_table_with_headers(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = '''
            <html><body>
            <table class="test">
                <thead>
                    <tr><th>Header 1</th><th>Header 2</th></tr>
                </thead>
                <tbody>
                    <tr><td>Row 1 Col 1</td><td>Row 1 Col 2</td></tr>
                    <tr><td>Row 2 Col 1</td><td>Row 2 Col 2</td></tr>
                </tbody>
            </table>
            </body></html>
        '''

        scrapper = UrlScrapper("http://example.com", "test", True)
        rows, headers = scrapper.extract_table()

        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], "Header 1")
        self.assertEqual(len(rows), 2)

    @patch('requests.get')
    def test_process_rows(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = '''
            <html><body>
            <table class="test">
                <thead>
                    <tr><th>Header 1</th><th>Header 2</th></tr>
                </thead>
                <tbody>
                    <tr><td>Row 1 Col 1</td><td>Row 1 Col 2</td></tr>
                    <tr><td>Row 2 Col 1</td><td>Row 2 Col 2</td></tr>
                </tbody>
            </table>
            </body></html>
        '''

        scrapper = UrlScrapper("http://example.com", "test", True)
        df = scrapper.process_rows()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))  # 2 rows, 2 columns
        self.assertListEqual(list(df.columns), ["Header 1", "Header 2"])
        self.assertEqual(df.iloc[0, 0], "Row 1 Col 1")


if __name__ == '__main__':
    unittest.main()
