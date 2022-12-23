from environment import Environment
from common.source_location import SourceLocation
from common.logger import CommonLogger
from urllib.parse import urlparse
import os
from pathlib import Path
import boto3


class CommonHelper:
    logger = CommonLogger()

    def get_source_location(self, text):
        try:
            if self._is_url(text):
                return SourceLocation.URL
            if os.path.exists(text) or Path(text).exists():
                return SourceLocation.FILE_SYSTEM
            if self._is_s3_path(
                text,
                s3_access_key=Environment.s3_access_key,
                s3_secret_key=Environment.s3_secret_key,
            ):
                return SourceLocation.S3
            return None
        except ValueError as e:
            self.logger.error(e)
            return False

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

    def _is_s3_path(self, text, s3_access_key=None, s3_secret_key=None):
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
