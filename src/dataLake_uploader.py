from io import BytesIO
import  json
from azure.storage.filedatalake import DataLakeServiceClient

class DataLakeUploader:
    def __init__(self, account_url, filesystem_name) -> object:
        """

        :rtype: object
        """
        self.service_client = DataLakeServiceClient(account_url=account_url)
        self.filesystem_client = self.service_client.get_file_system_client(filesystem_name)

    def upload_data_from_str(self, file_name, data):
        """Uploads data as a string (e.g., CSV or JSON) to the Data Lake."""
        file_client = self.filesystem_client.get_file_client(file_name)
        csv_bytes = BytesIO(data.encode('utf-8'))
        file_client.upload_data(csv_bytes.getvalue(), overwrite=True)
        csv_bytes.close()
        print(f"CSV data uploaded to {file_name} in filesystem.")

    def upload_csv_from_dataframe(self, file_name, dataframe):
        """Uploads a DataFrame as a CSV file to the Data Lake."""
        csv_buffer = BytesIO()
        dataframe.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Reset buffer position to the beginning
        file_client = self.filesystem_client.get_file_client(file_name)
        file_client.upload_data(csv_buffer.getvalue(), overwrite=True)
        csv_buffer.close()
        print(f"CSV DataFrame uploaded to {file_name} in filesystem.")

    def upload_json(self, file_name, data):
        """Uploads JSON data to the Data Lake."""
        json_str = json.dumps(data)
        json_bytes = BytesIO(json_str.encode('utf-8'))
        file_client = self.filesystem_client.get_file_client(file_name)
        file_client.upload_data(json_bytes, overwrite=True)
        #json_str.close()
        print(f"JSON data uploaded to {file_name} in filesystem.")