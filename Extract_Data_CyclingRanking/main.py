from Extract_Data_CyclingRanking.storage_acoount_sas_details import sas_token, storage_account_name
from Scraper import CyclingDataScraper
from DataLakeUploader import DataLakeUploader



def run(scraper, uploader, blob_name, with_headers):
    print("Scraping data...")
    csv_data = scraper.process_ranking_rows(with_headers, limit=20)
    print("Uploading data to Azure Data Lake...")
    uploader.upload_data(blob_name, csv_data)
    print("Pipeline completed.")

if __name__ == "__main__":
    # Define variables
    account_url = f"https://{storage_account_name}.dfs.core.windows.net/?{sas_token}"
    table_class = "table table-striped"
    folder = "raw/test"
    for year in range(2009, 2010):
        URL = f"https://www.cyclingranking.com/riders/{year}"
        BLOB_NAME = f"riders_data_streamed{year}.csv"
        scrapper = CyclingDataScraper(URL, table_class)
        uploader = DataLakeUploader(account_url, folder)
    # Run the data pipeline
        #pipeline = RidersDataPipeline(URL, BLOB_NAME)
        run(scrapper, uploader, BLOB_NAME, False)
