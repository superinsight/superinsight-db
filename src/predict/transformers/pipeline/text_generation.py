import logging
from storage.model import StorageModel

class TextGenerationPipeline:

    logger = None
    pipeline = None
    model_path = None
    storage_model = StorageModel()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu = False):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.logger.info(
          "TextGenerationPipeline init model_path:{}".format(str(self.model_path)))
      self.model_path = model_path
      self.pipeline = self.storage_model.getPipeline(task = "text-generation", model_path = self.model_path, use_gpu = use_gpu)

    def __del__(self):
      self.logger.info(
          "TextGenerationPipeline existing model_path:{}".format(str(self.model_path)))

    def exec(self, prompt, max_length, min_length):
        print(prompt, max_length, min_length)
        return self.pipeline(prompt, max_length=max_length, min_length=min_length, do_sample=False)
