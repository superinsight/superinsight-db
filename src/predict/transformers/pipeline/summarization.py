import logging
from storage.model import StorageModel


class SummarizationPipeline:

    logger = None
    pipeline = None
    tokenizer = None
    model_path = None
    storage_model = StorageModel()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu = False):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if handler is not None:
            self.logger.addHandler(handler)
        self.logger.info(
            "SummarizationPipeline init model_path:{}".format(str(self.model_path)))
        self.model_path = model_path
        self.pipeline = self.storage_model.getPipeline(task = "summarization", model_path = self.model_path, use_gpu = use_gpu)
        self.tokenizer = self.storage_model.getTokenizer(task = "summarization", model_path = self.model_path, model_type=None)

    def __del__(self):
        self.logger.info(
            "SummarizationPipeline existing model_path:{}".format(str(self.model_path)))

    def exec(self, article, max_length, min_length):
        if max_length is None or max_length == 0:
            max_length = len(self.tokenizer.tokenize(article))
        if min_length > max_length:
            return [{ "summary_text" : article}]
        else:
            return self.pipeline(article, max_length=max_length, min_length=min_length, do_sample=False)
