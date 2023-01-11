from storage.model import StorageModel
from storage.model_types import ModelTypes
from common.helper import CommonHelper
from common.source_location import SourceLocation
import torch
import hashlib
from PIL import Image
from common.logger import CommonLogger


class ImageToTextPipeline:

    logger = None
    pipeline = None
    tokenizer = None
    model_path = None
    device = None
    storage_model = StorageModel()
    logger = CommonLogger()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu=False):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info(
            "ImageToTextPipeline init model_path:{}".format(str(self.model_path))
        )
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.storage_model.getModel(
            task="image_to_text",
            model_type=ModelTypes.VISION_ENCODER_DECODER.value,
            model_path=self.model_path,
            use_gpu=use_gpu,
        )
        self.tokenizer = self.storage_model.getTokenizer(
            task="image_to_text",
            model_type=ModelTypes.VISION_ENCODER_DECODER.value,
            model_path=self.model_path,
            use_gpu=use_gpu,
        )
        self.feature_extractor = self.storage_model.getFeatureExtractor(
            task="image_to_text",
            model_type=ModelTypes.VISION_ENCODER_DECODER.value,
            model_path=self.model_path,
            use_gpu=use_gpu,
        )
        self.model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    def __del__(self):
        self.logger.info(
            "ImageToTextPipeline existing model_path:{}".format(str(self.model_path))
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
        text = self.__predict(image_path=image_path)
        return {"text": text}

    def __predict(self, image_path):
        max_length = 16
        num_beams = 4
        gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert(mode="RGB")
        pixel_values = self.feature_extractor(
            images=[image], return_tensors="pt"
        ).pixel_values
        pixel_values = pixel_values.to(self.device)
        output_ids = self.model.generate(pixel_values, **gen_kwargs)
        preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        return preds[0]
