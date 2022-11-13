import logging
import requests
import json
from environment import Environment

class TranslationPipeline:

	logger = None
	provider = None

	def __init__(self, logger=None, handler=None, provider=None):
		self.logger = logger or logging.getLogger(__name__)
		self.logger.setLevel(logging.INFO)
		if handler is not None:
			self.logger.addHandler(handler)
		self.logger.info(
		    "Init ML.Pipeline.Translation for provider:{}".format(str(provider)))
		self.provider = provider

	def __del__(self):
		self.logger.info("Exit ML.Pipeline.Translation...")

	def run(self, input, src_lang, tgt_lang):
		return self.__run_superinsight(input=input, src_lang=src_lang, tgt_lang=tgt_lang)

	def __run_superinsight(self, input, src_lang, tgt_lang):
		model_inputs = {
        	"model_type": Environment.default_model_type_translation,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "inputs":  input,
            "model": Environment.default_model_translation,
            "options": {"use_gpu": False, "wait_for_model": True}
		}
		self.logger.info(
		    "Init ML.Pipeline.Translation.__run_superinsight:model_inputs", model_inputs)
		url = "{}/translation".format(Environment.provider_api_url_superinsight)
		response = requests.request("POST", url, data=json.dumps(model_inputs), headers={
		                            "accept": "application/json", "Content-Type": "application/json"})
		model_output = response.json()
		self.logger.info(
		    "Init ML.Pipeline.Translation.__run_superinsight:model_output")
		self.logger.info(json.dumps({"model_output": model_output}))
		return model_output[0]["translation_text"]
