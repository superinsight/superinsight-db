import logging
import requests
import json
from environment import Environment
class TextGenerationPipeline:

    logger = None
    provider = None

    def __init__(self, logger=None, handler = None, provider = None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.provider = provider
      self.logger.info("Init ML.Pipeline.TextGeneration for provider:{}".format(str(provider)))

    def __del__(self):
      self.logger.info("Exit ML.Pipeline.TextGeneration...")

    def run(self, prompt, max_length, min_length):
      return self.__run_superinsight(prompt = prompt, max_length=max_length, min_length=min_length)

    def __run_superinsight(self, prompt, max_length, min_length):
      model_inputs = {
          "inputs":  prompt,
          "model": Environment.default_model_text_generation, 
          "max_length": max_length,
          "min_length": min_length,
          "options": {
            "use_gpu": False,
            "wait_for_model": True
          }
      }
      self.logger.info("Init ML.Pipeline.TextGeneration.__run_superinsight:model_inputs", model_inputs)
      url = "{}/text-generation".format(Environment.provider_api_url_superinsight)
      response = requests.request("POST", url, data=json.dumps(model_inputs), headers = {"accept": "application/json", "Content-Type": "application/json" })
      model_output = response.json()
      self.logger.info("Init ML.Pipeline.TextGeneration.__run_superinsight:model_output")
      self.logger.info(json.dumps({"model_output":model_output}))
      return model_output["output"]