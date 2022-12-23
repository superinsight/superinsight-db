import requests
import json
from environment import Environment
from common.logger import CommonLogger
from common.helper import CommonHelper
from common.source_location import SourceLocation


class ImageToTextPipeline:
    logger = CommonLogger()

    def generate(self, text):
        self.logger.info("ImageToTextPipeline.generate", text)
        source_location = CommonHelper().get_source_location(text)
        if source_location is not None:
            texts = []
            image_text = self.__imageToText(image_source=text)
            if image_text is not None and image_text.get("text") is not None:
                texts.append(image_text["text"])
            image_tags = self.__imageToTags(image_source=text)
            labels = []
            if (
                image_tags is not None
                and len(image_tags) > 0
                and isinstance(image_tags, list)
            ):
                labels = [o["label"] for o in image_tags][0:3]
            return (texts, labels)
        else:
            return (None, None)

    def __imageToText(self, image_source):
        self.logger.info("ImageToTextPipeline.__imageToText", image_source)
        if Environment.index_image_to_caption is False:
            return None
        payload = json.dumps(
            {
                "inputs": image_source,
                "model": Environment.image_to_text_model,
                "options": {"use_gpu": False, "wait_for_model": True},
            }
        )
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        url = "{}/image-to-text".format(Environment.host_ml_inference)
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def __imageToTags(self, image_source):
        self.logger.info("ImageToTextPipeline.__imageToTags", image_source)
        if Environment.index_image_to_label is False:
            return None
        payload = json.dumps(
            {
                "inputs": image_source,
                "model": Environment.image_classification_model,
                "options": {"use_gpu": False, "wait_for_model": True},
            }
        )
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        url = "{}/image-classification".format(Environment.host_ml_inference)
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
