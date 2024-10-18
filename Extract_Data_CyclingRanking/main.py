from Extract_Data_CyclingRanking.storage_acoount_sas_details import sas_token, storage_account_name
from Scraper import RiderDataScraper
from DataLakeUploader import DataLakeUploader

class RidersDataPipeline:
    def __init__(self, scraper_url, blob_name):
        account_url = f"https://{storage_account_name}.dfs.core.windows.net/?{sas_token}"
        self.scraper = RiderDataScraper(scraper_url)
        self.uploader = DataLakeUploader(account_url, "raw")
        self.blob_name = blob_name

    def run(self):
        print("Scraping data...")
        csv_data = self.scraper.extract_rider_data(limit=20)

        print("Uploading data to Azure Data Lake...")
        self.uploader.upload_data(self.blob_name, csv_data)

        print("Pipeline completed.")


if __name__ == "__main__":
    # Define variables
    for year in range(2009, 2025):
        URL = f"https://www.cyclingranking.com/riders/{year}"
        BLOB_NAME = f"riders_data_streamed{year}.csv"

    # Run the data pipeline
        pipeline = RidersDataPipeline(URL, BLOB_NAME)
        pipeline.run()
