# from src.tour_stage_scrapper import TourRaceScrapper
from types import NoneType

from black.lines import Index

from src.races_scrapper import RacesScrapper
from src.one_day_race_scrapper import OneDayRaceScrapper
from src.dataLake_uploader import DataLakeUploader
from config.settings import storage_account_name, sas_token
from src.tour_scrapper_info import TourScrapperInfo
from src.tour_stage_scrapper import TourStageScrapper
from src.scrapper import UrlScrapper

def scrape_ranking(url, data_lake_uploader, year):
    ranking_scrapped = UrlScrapper(url, "table table-striped", True)
    ranking = ranking_scrapped.process_rows()
    ranking['Rider'] = ranking['Rider'].apply(lambda x: x.split('\n')[0])

    data_lake_uploader.upload_csv_from_dataframe(f"ranking/{year}/ranking_classification.csv", ranking)

def scrape_races(url, data_lake_uploader, year):
    """Scrape the race information from the provided URL."""
    race_scrapper = RacesScrapper(url, "basic", with_header=True)
    df_races, df_links = race_scrapper.process_rows()

    # Upload the races DataFrame to Data Lake
    data_lake_uploader.upload_csv_from_dataframe(f"races_list/{year}/list.csv", df_races)

    return df_links

def process_race(df_link_row, data_lake_uploader, year):
    """Process each race link for one-day or multi-stage races."""

    # if df_link_row['Is_one_day_race']:
    #     one_day_race_scrapper = OneDayRaceScrapper(
    #         df_link_row['Link'], "results basic moblist10", "infolist", True
    #     )
    #     results_and_infos = one_day_race_scrapper.stage_process()
    #     #return results_and_infos
    #     # Create folder and upload file
    #     data_lake_uploader.upload_json(f"/{year}/races/results.json", results_and_infos)
    link = df_link_row['Link']
    race_name = df_link_row['Race_Name']
    if df_link_row['Is_one_day_race']:
        one_day_race_scrapper = OneDayRaceScrapper(
            link, "results basic moblist10", "infolist", True
        )
        try:
            results_and_infos = one_day_race_scrapper.stage_process()
            data_lake_uploader.upload_json(f"races/{race_name}/{year}/results.json", results_and_infos)
        except AttributeError:
            print(link)
            print('race cancelled')
        # Create folder and upload file

    else:
        tour_scrapper = TourScrapperInfo(
            link, "results basic moblist10", "pageSelectNav", True
        )
        try:
            final_classifications = tour_scrapper.get_classification_tables()
            stages = tour_scrapper.get_stages_selector()

            # upload final result classification
            data_lake_uploader.upload_json(f"races/{race_name}/{year}/general_classification.json", final_classifications)


            for stage in stages:
                stage_race = TourStageScrapper(
                    stage['url'], "results basic moblist10", "infolist", True
                )
                try:
                    stage_results_and_infos = stage_race.stage_process()
                    stage_nbr = stage['name'][:8].strip().replace(' ', '')
                    data_lake_uploader.upload_json(f"races/{race_name}/{year}/{stage_nbr}.json", stage_results_and_infos)
                except IndexError:
                    print(stage['url'])
                    print("stage cancelled")
        except AttributeError:
            print(link)
            print("Race Cancelled")


#2023, 2022, 2021, 2020, 2019 , 2018, 2017, 2016, 2015, 2014, 2013, 2012 ok

#year = 2024
for year in range(2011, 2025):
    url = f"https://www.procyclingstats.com/races.php?year={year}&circuit=1"
    url2 = f"https://www.cyclingranking.com/riders/{year}"

    account_url = f"https://{storage_account_name}.dfs.core.windows.net/?{sas_token}"
    data_lake_uploader = DataLakeUploader(account_url, "/raw/")

    scrape_ranking(url2, data_lake_uploader, year)
    races = RacesScrapper(url, "basic", True)
    df_races, df_links = races.process_rows()
    #for year in range(2017, 2025):
    df_links = scrape_races(url, data_lake_uploader, year)
    for i in range(len(df_links)):
        process_race(df_links.iloc[i], data_lake_uploader,  year)
    print("Finished")


