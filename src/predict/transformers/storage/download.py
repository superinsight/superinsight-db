import os
import shutil
from pathlib import Path
import hashlib
from google.cloud import storage
modelRepository = os.getenv("LOCAL_MODEL_REPOSITORY", "./models")


class StorageDownload:

    logger = None
    model_path = None
    model_directory = None

    def downloadModel(self, model_path, refresh=False):
        model_id = hashlib.sha1(model_path.encode()).hexdigest()
        self.model_directory = "{}/{}".format(modelRepository, model_id)
        bucketName = model_path.split("://")[1].split("/")[0]
        source_folder = "/".join(model_path.split("://")[1].split("/")[1:])
        if refresh is False and os.path.exists(self.model_directory):
            return "{}/{}".format(self.model_directory, source_folder)
        if refresh is True and os.path.exists(self.model_directory):
            shutil.rmtree(self.model_directory)
        self.__downloadFolder(
            bucket_name=bucketName,  source_folder=source_folder, destination_folder=self.model_directory)
        return "{}/{}".format(self.model_directory, source_folder)

    def __downloadObject(self, bucket_name, source_blob_name, destination_file_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        parent = Path(destination_file_name).parent
        Path(parent).mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(destination_file_name)

    def __downloadFolder(self, bucket_name, source_folder, destination_folder):
        Path(destination_folder).mkdir(parents=True, exist_ok=True)
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=source_folder)
        for blob in blobs:
            self.__downloadObject(bucket_name, blob.name,
                                  "{}/{}".format(destination_folder, blob.name))
