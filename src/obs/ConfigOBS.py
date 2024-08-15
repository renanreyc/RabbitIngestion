import boto3
from io import BytesIO, StringIO
import logging
import os

from utils.utils import Utils

class OBS:
    def __init__(self):
        self._logger = logging.getLogger(name="Huawei OBS Tools")
        self._aws_access_key_id = os.environ.get("aws_access_key_id", '.env') 
        self._aws_secret_access_key = os.environ.get("aws_secret_access_key", '.env')
        self._endpoint_url = os.environ.get("aws_endpoint_url", '.env')
        self._region_name = os.environ.get("aws_region_name", '.env')
        self.aws_s3_allow_unsafe_rename = os.environ.get("aws_s3_allow_unsafe_rename", '.env')

        self.BUCKET_NAME = os.environ.get("aws_bucket_name", '.env')
        self.BUCKET_TMP_NAME = os.environ.get("aws_bucket_temp_name", ".env")
        
        self._utils = Utils()
        self._utils.start_logging('Huawei OBS Tools')

    def create_obs_session(self):
        try:
            self._utils.logging_status("Creating Boto3 Session for OBS service.")
            session = boto3.session.Session()

            client_obs = session.client(
                service_name='s3',
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key,
                endpoint_url=self._endpoint_url,
                region_name=self._region_name)
            self._utils.logging_status("Boto3 session created for OBS service successfully!")

            return client_obs

        except Exception as error:
            self._logger.exception(error)
            return False

    def upload_object(self, file_path_out, content, bucket_name = None):
        bucket_name = self.BUCKET_NAME if bucket_name == None else bucket_name

        self._utils.logging_status(f"Uploading object {file_path_out} to OBS.")
        try:
            client_obs = self.create_obs_session()
            
            client_obs.put_object(Bucket=bucket_name, Key=file_path_out, Body=content)
            self._utils.logging_status(f"Object {file_path_out} sent to OBS.")

        except Exception as error:
            self._logger.exception(error)
            raise
    
    def upload_file(self, file_path_in, file_path_out, bucket_name = None):
        bucket_name = self.BUCKET_NAME if bucket_name == None else bucket_name

        self._utils.logging_status(f"Uploading file {file_path_in} to OBS.")
        try:
            client_obs = self.create_obs_session()           
            with open(file_path_in, 'rb') as file:
                client_obs.upload_fileobj(file, Bucket=bucket_name, Key=file_path_out)
            
            self._utils.logging_status(f"File {file_path_out} writed to OBS.")

        except Exception as error:
            self._logger.exception(error)
            raise

        
    def download_file(self, file_path_out, bucket_name = None):
        bucket_name = self.BUCKET_NAME if bucket_name == None else bucket_name

        self._utils.logging_status(f"Downloading file {file_path_out} from OBS.")
        try:
            client_obs = self.create_obs_session()
            buffer = BytesIO()
            
            client_obs.download_fileobj(Bucket=bucket_name, Key=file_path_out, Fileobj=buffer)
            buffer.seek(0)  

            self._utils.logging_status(f"File {file_path_out} downloaded from OBS.")
            return buffer

        except Exception as error:
            self._logger.exception(error)
            return False

# Example usage:
# obs_instance = OBS()
# obs_instance.upload_file('file_path_out', 'file_content')
