import logging
from storage.model import StorageModel


class ZeroShotClassificationPipeline:

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
            "ZeroShotClassificationPipeline init model_path:{}".format(str(self.model_path)))
        self.model_path = model_path
        self.pipeline = self.storage_model.getPipeline(task = "zero-shot-classification", model_path = self.model_path, use_gpu = use_gpu)

    def __del__(self):
        self.logger.info(
            "ZeroShotClassificationPipeline existing model_path:{}".format(str(self.model_path)))

    def exec(self, inputs, labels):
        return self.pipeline(inputs, labels)