import logging
from storage.model import StorageModel
from storage.model_types import ModelTypes
from common.helper import CommonHelper
from common.source_location import SourceLocation
import torch
from PIL import Image
from transformers import pipeline
from common.logger import CommonLogger


class ImageClassificationPipeline:

    logger = None
    model_path = None
    pipeline = None
    device = None
    storage_model = StorageModel()
    logger = CommonLogger()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu=False):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info(
            "ImageClassificationPipeline init model_path:{}".format(
                str(self.model_path)
            )
        )
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.storage_model.getModel(
            task="image_classification",
            model_type=ModelTypes.IMAGE_CLASSIFICATION.value,
            model_path=self.model_path,
            use_gpu=use_gpu,
        )
        self.feature_extractor = self.storage_model.getFeatureExtractor(
            task="image_classification",
            model_type=ModelTypes.IMAGE_CLASSIFICATION.value,
            model_path=self.model_path,
            use_gpu=use_gpu,
        )
        self.model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        self.pipeline = pipeline(
            "image-classification",
            model=self.model,
            feature_extractor=self.feature_extractor,
        )

    def __del__(self):
        self.logger.info(
            "ImageClassificationPipeline existing model_path:{}".format(
                str(self.model_path)
            )
        )

    def exec(self, inputs):
        common_helper = CommonHelper()
        source_location = common_helper.get_source_location(inputs)
        image_path = None
        if source_location == SourceLocation.URL:
            image_path = common_helper.localize_file_from_url(target=inputs)
        if source_location == SourceLocation.FILE_SYSTEM:
            image_path = common_helper.localize_file_from_file_system(target=inputs)
        if source_location == SourceLocation.S3:
            image_path = common_helper.localize_file_from_s3(target=inputs)
        if image_path is None:
            return None
        with Image.open(image_path) as image:
            return self.pipeline(image)
