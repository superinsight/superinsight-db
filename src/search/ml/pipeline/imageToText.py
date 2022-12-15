import validators
import requests
import json
from environment import Environment


class ImageToTextPipeline:

    def generate(self, text):
        if validators.url(text):
            texts = []
            image_text = self.__imageToText(image_url=text)
            if image_text is not None and image_text.get('text') \
                is not None:
                texts.append(image_text['text'])
            image_tags = self.__imageToTags(image_url=text)
            labels = []
            if image_tags is not None and len(image_tags) > 0 \
                and isinstance(image_tags, list):
                labels = [o['label'] for o in image_tags][0:3]
            return (texts, labels)
        else:
            return (None, None)

    def __imageToText(self, image_url):
        if Environment.index_image_to_caption is False:
            return None
        payload = json.dumps({'inputs': image_url,
                             'model': Environment.image_to_text_model,
                             'options': {'use_gpu': False,
                             'wait_for_model': True}})
        headers = {'accept': 'application/json',
                   'Content-Type': 'application/json'}
        url = '{}/image-to-text'.format(Environment.host_ml_inference)
        response = requests.request('POST', url, headers=headers,
                                    data=payload)
        return response.json()

    def __imageToTags(self, image_url):
        if Environment.index_image_to_label is False:
            return None
        payload = json.dumps({'inputs': image_url,
                             'model': Environment.image_classification_model,
                             'options': {'use_gpu': False,
                             'wait_for_model': True}})
        headers = {'accept': 'application/json',
                   'Content-Type': 'application/json'}
        url = \
            '{}/image-classification'.format(Environment.host_ml_inference)
        response = requests.request('POST', url, headers=headers,
                                    data=payload)
        return response.json()
