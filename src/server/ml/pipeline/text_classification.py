import logging
import requests
import json
from environment import Environment
class TextClassificationPipeline:

    logger = None
    provider = None

    def __init__(self, logger=None, handler = None, provider = None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.provider = provider
      self.logger.info("TextClassificationPipeline init for provider:{}".format(str(self.provider)))

    def __del__(self):
      self.logger.info("TextClassificationPipeline exiting for provider:{}".format(str(self.provider)))

    def run(self, inputs, labels):
      return self.__run_superinsight(inputs = inputs, labels = labels)

    def __run_superinsight(self, inputs = None, labels = []):
      model_inputs = {
          "inputs":  inputs,
          "model": Environment.default_model_text_classification, 
          "parameters": {"candidate_labels": labels },
          "options": {
            "use_gpu": False,
            "wait_for_model": True
          }
      }
      self.logger.info("Init ML.Pipeline.TextClassification.__run_superinsight:model_inputs", model_inputs)
      url = "{}/zero-shot-classification".format(Environment.provider_api_url_superinsight)
      response = requests.request("POST", url, data=json.dumps(model_inputs), headers = {"accept": "application/json", "Content-Type": "application/json" })
      model_output = response.json()
      self.logger.info("Init ML.Pipeline.TextClassification.__run_superinsight:model_output")
      self.logger.info(json.dumps({"model_output":model_output}))
      return model_output