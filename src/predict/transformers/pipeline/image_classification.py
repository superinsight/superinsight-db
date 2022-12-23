import logging
from storage.model import StorageModel
from storage.model_types import ModelTypes
import validators
import torch
from PIL import Image
import requests
import io
import os, shutil, hashlib
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
        if validators.url(inputs):
            image_path = self.__localizeFile(url=inputs)
            with Image.open(image_path) as image:
                return self.pipeline(image)
        else:
            return None

    def __localizeFile(self, url):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            image_dir = "/tmp/{}".format(hashlib.md5(url.encode()).hexdigest())
            if os.path.isdir(image_dir) == True:
                shutil.rmtree(image_dir)
            os.makedirs(image_dir)
            image_path = "{}/image.png".format(image_dir)
            image = Image.open(io.BytesIO(response.content))
            image.save(image_path)
            return image_path
        else:
            return None
