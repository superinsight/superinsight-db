import logging
from storage.model import StorageModel
from storage.model_types import ModelTypes
import validators
import requests
import io
import os, shutil, hashlib
import torch
import hashlib
from PIL import Image


class ImageToTextPipeline:

    logger = None
    pipeline = None
    tokenizer = None
    model_path = None
    device= None
    storage_model = StorageModel()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu=False):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if handler is not None:
            self.logger.addHandler(handler)
        self.logger.info(
            "ImageToTextPipeline init model_path:{}".format(str(self.model_path)))
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.storage_model.getModel(task = "image_to_text", model_type = ModelTypes.VISION_ENCODER_DECODER.value, model_path = self.model_path, use_gpu=use_gpu)
        self.tokenizer = self.storage_model.getTokenizer(task = "image_to_text", model_type = ModelTypes.VISION_ENCODER_DECODER.value, model_path = self.model_path, use_gpu=use_gpu)
        self.feature_extractor = self.storage_model.getFeatureExtractor(task = "image_to_text", model_type = ModelTypes.VISION_ENCODER_DECODER.value, model_path = self.model_path, use_gpu=use_gpu)
        self.model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
 
    def __del__(self):
        self.logger.info(
            "ImageToTextPipeline existing model_path:{}".format(str(self.model_path)))

    def exec(self, inputs):
        if validators.url(inputs):
            local_path = self.__localizeFile(url=inputs)
            text = self.__predict(image_path = local_path)
            return { "text" : text }
        else:
            return None

    def __predict(self, image_path):
        max_length = 16
        num_beams = 4
        gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert(mode="RGB")
        pixel_values = self.feature_extractor(images=[image], return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)
        output_ids = self.model.generate(pixel_values, **gen_kwargs)
        preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        return preds[0]

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