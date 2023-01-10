from storage.model import StorageModel
from common.helper import CommonHelper
from common.source_location import SourceLocation
from common.logger import CommonLogger
import os, shutil, tempfile, io
from PyPDF2 import PdfReader
import ocrmypdf


class PdfToTextPipeline:

    logger = None
    model_path = None
    device = None
    storage_model = StorageModel()
    logger = CommonLogger()

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("PdfToTextPipeline init")

    def __del__(self):
        self.logger.info("PdfToTextPipeline existing")

    def exec(self, inputs):
        common_helper = CommonHelper()
        source_location = common_helper.get_source_location(inputs)
        source_file = None
        if source_location == SourceLocation.URL:
            source_file = common_helper.localize_file_from_url(target=inputs)
        if source_location == SourceLocation.FILE_SYSTEM:
            source_file = common_helper.localize_file_from_file_system(target=inputs)
        if source_location == SourceLocation.S3:
            source_file = common_helper.localize_file_from_s3(target=inputs)
        if source_file is None:
            return None
        texts = self.parse(source_file=source_file)
        return texts

    def _ocr(self, source_file):
        try:
            temp_dir = tempfile.mkdtemp()
            temp_file = "{}/{}".format(temp_dir, source_file.split("/")[-1])
            ocrmypdf.ocr(source_file, temp_file, deskew=True, skip_text=True)
            return temp_file
        except ValueError as e:
            self.logger.error(e)
            return source_file

    def parse(self, source_file):
        try:
            texts = []
            source_file = self._ocr(source_file)
            with open(source_file, "rb") as file:
                reader = PdfReader(file)
                num_pages = len(reader.pages)
                for i in range(num_pages):
                    page = reader.pages[i]
                    text = page.extract_text()
                    texts.append(text)
            return texts
        except ValueError as e:
            self.logger.error(e)
            return texts
