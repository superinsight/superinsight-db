import logging
import requests
import json
from environment import Environment

class QuestionAnsweringPipeline:

    logger = None
    provider = None

    def __init__(self, logger=None, handler=None, provider=None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.provider = provider
      self.logger.info(
          "Init ML.Pipeline.QuestionAnswering for provider:{}".format(str(provider)))

    def __del__(self):
      self.logger.info("Exit ML.Pipeline.QuestionAnswering...")

    def run(self, context, question):
      return self.__run_superinsight(context=context, question=question)

    def __run_superinsight(self, context=None, question=None):
      model_inputs = {
          "model": Environment.default_model_question_answering, 
          "inputs": {
              "context":  context,
              "question":  question
          },
          "options": {
              "use_gpu": False,
              "wait_for_model": True
          }
      }
      self.logger.info(
          "Init ML.Pipeline.QuestionAnswering.__run_superinsight:model_inputs", model_inputs)
      url = "{}/question-answering".format(
          Environment.provider_api_url_superinsight)
      response = requests.request("POST", url, data=json.dumps(model_inputs), headers={
                                  "accept": "application/json", "Content-Type": "application/json"})
      model_output = response.json()
      self.logger.info(
          "Init ML.Pipeline.QuestionAnswering.__run_superinsight:model_output")
      self.logger.info(json.dumps({"model_output": model_output}))
      return model_output