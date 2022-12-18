from common.logger import CommonLogger
import requests
import json
from environment import Environment


class SummarizationPipeline:

    logger = CommonLogger()
    provider = None

    def __init__(self, logger=None, handler=None, provider=None):
        self.logger.info(
            "Init ML.Pipeline.Summarization for provider:{}".format(str(provider))
        )
        self.provider = provider

    def __del__(self):
        self.logger.info("Exit ML.Pipeline.Summarization...")

    def run(self, input, min_length):
        return self.__run_superinsight(input, min_length=min_length)

    def __run_superinsight(self, input, min_length):
        model_inputs = {
            "inputs": input,
            "model": Environment.default_model_summarization,
            "min_length": min_length,
            "options": {"use_gpu": False, "wait_for_model": True},
        }
        self.logger.info(
            "Init ML.Pipeline.Summarization.__run_superinsight:model_inputs",
            model_inputs,
        )
        url = "{}/summarization".format(Environment.provider_api_url_superinsight)
        response = requests.request(
            "POST",
            url,
            data=json.dumps(model_inputs),
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )
        model_output = response.json()
        self.logger.info(
            "Init ML.Pipeline.Summarization.__run_superinsight:model_output"
        )
        self.logger.info(json.dumps({"model_output": model_output}))
        return model_output[0]
