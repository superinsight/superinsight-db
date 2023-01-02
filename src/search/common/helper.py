from environment import Environment
from common.source_location import SourceLocation
from common.logger import CommonLogger
from urllib.parse import urlparse
import os
from pathlib import Path
import boto3
import urllib.request
import os, shutil, tempfile, io, re
import requests
from PIL import Image


class CommonHelper:
    logger = CommonLogger()

    def get_source_location(self, text):
        try:
            if self._is_url(text):
                return SourceLocation.URL
            if re.match(r"^([^ ]*)+?$", text) and (
                os.path.exists(text) or Path(text).exists()
            ):
                return SourceLocation.FILE_SYSTEM
            if self._is_s3_path(text):
                return SourceLocation.S3
            return None
        except ValueError as e:
            self.logger.error(e)
            return False

    def localize_file_from_url(self, target):
        response = requests.get(target, stream=True)
        temp_dir = tempfile.mkdtemp()
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            image_path = "{}/image.png".format(temp_dir)
            image.save(image_path)
            return image_path
        else:
            return None

    def localize_file_from_file_system(self, target):
        temp_dir = tempfile.mkdtemp()
        filename = os.path.basename(target)
        shutil.copy(target, temp_dir)
        return "{}/{}".format(temp_dir, filename)

    def localize_file_from_s3(self, target, s3_access_key=None, s3_secret_key=None):
        temp_dir = tempfile.mkdtemp()
        if self._is_s3_path(target) is False:
            return False
        client = boto3.client(
            "s3", aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key
        )
        parsed_url = urllib.parse.urlparse(target)
        bucket_name = parsed_url.netloc
        object_key = parsed_url.path.lstrip("/")
        download_path = "{}/{}".format(temp_dir, object_key)
        client.download_file(bucket_name, object_key, download_path)
        return download_path

    def _is_url(self, text):
        try:
            result = urlparse(text)
            return (
                all([result.scheme, result.netloc])
                and result.scheme != "file"
                and result.scheme != "s3"
            )
        except ValueError as e:
            self.logger.error(e)
            return False

    def _is_s3_path(self, text):
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc]) and result.scheme == "s3"
        except ValueError as e:
            self.logger.error(e)
            return False

    def _is_s3_path_valid(self, text, s3_access_key=None, s3_secret_key=None):
        if self._is_s3_path(text) is False:
            return False
        client = boto3.client(
            "s3", aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key
        )
        try:
            bucket, key = text.replace("s3://", "", 1).split("/", 1)
            client.head_object(Bucket=bucket, Key=key)
            return True
        except client.exceptions.ClientError as e:
            self.logger.error(e)
            return False
