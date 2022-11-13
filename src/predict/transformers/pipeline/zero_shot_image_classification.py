import logging
from storage.model import StorageModel
from storage.model_types import ModelTypes
from PIL import Image
import requests
import torch

class ZeroShotImageClassificationPipeline:

    logger = None
    model = None
    processor = None
    model_path = None
    device = None
    storage_model = StorageModel()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu = False):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if handler is not None:
            self.logger.addHandler(handler)
        self.logger.info(
            "ZeroShotImageClassificationPipeline init model_path:{}".format(str(self.model_path)))
        self.model_path = model_path
        self.model = self.storage_model.getModel(task = "zero_shot_image_classification", model_type = ModelTypes.ZERO_SHOT_IMAGE_CLASSIFICATION.value, model_path = self.model_path, use_gpu=use_gpu)
        self.processor = self.storage_model.getProcessor(task = "zero_shot_image_classification", model_type = ModelTypes.ZERO_SHOT_IMAGE_CLASSIFICATION.value, model_path = self.model_path, use_gpu=use_gpu)

    def __del__(self):
        self.logger.info(
            "ZeroShotImageClassificationPipeline existing model_path:{}".format(str(self.model_path)))

    def exec(self, url, labels):
        image = Image.open(requests.get(url, stream=True).raw)
        inputs = self.processor(text=labels, images=image, return_tensors="pt", padding=True)
        outputs = self.model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=-1)
        scores = probs.tolist()[0]
        return { "sequence": url, "labels": labels, "scores": scores }