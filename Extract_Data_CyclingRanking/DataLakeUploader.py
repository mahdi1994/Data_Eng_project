from azure.storage.filedatalake import DataLakeServiceClient
from io import BytesIO


class DataLakeUploader:
    def __init__(self, account_url, filesystem_name):
        self.service_client = DataLakeServiceClient(account_url=account_url)
        self.filesystem_client = self.service_client.get_file_system_client(filesystem_name)

    def upload_data(self, file_name, data):
        file_client = self.filesystem_client.get_file_client(file_name)
        csv_bytes = BytesIO(data.encode('utf-8'))
        file_client.upload_data(csv_bytes.getvalue(), overwrite=True)
        csv_bytes.close()
        print(f"CSV data uploaded to {file_name} in filesystem.")
