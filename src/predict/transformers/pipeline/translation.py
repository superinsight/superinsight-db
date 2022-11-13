import logging
from storage.model import StorageModel

class TranslationPipeline:

    logger = None
    pipeline = None
    model_path = None
    model = None
    model_type = None
    tokenizer = None
    storage_model = StorageModel()

    def __init__(self, logger=None, handler=None, model_path=None, model_type=None, use_gpu = False):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if handler is not None:
            self.logger.addHandler(handler)
        self.logger.info(
            "TranslationPipeline init model_path:{}".format(str(self.model_path)))
        self.model_path = model_path
        self.model_type = model_type
        if self.model_type is not None and self.model_type != "":
            self.tokenizer = self.storage_model.getTokenizer(task = "translation", model_path = self.model_path, model_type=self.model_type)
            self.model = self.storage_model.getModel(task = "translation", model_path = self.model_path, model_type=self.model_type, use_gpu = use_gpu)
        else:
            self.pipeline = self.storage_model.getPipeline(task = "translation", model_path = self.model_path, use_gpu = use_gpu)
            print("TranslationPipeline init model_path:{}".format(
                str(self.model_path)))

    def __del__(self):
        self.logger.info(
            "TranslationPipeline existing model_path:{}".format(str(self.model_path)))

    def exec(self, input, src_lang, tgt_lang):
        if self.pipeline is not None:
            return self.pipeline(input, src_lang=src_lang, tgt_lang=tgt_lang)
        else:
            self.tokenizer.src_lang = src_lang
            encoded_ar = self.tokenizer(input, return_tensors="pt")
            generated_tokens = self.model.generate(
                **encoded_ar,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang]
            )
            translation_texts = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
            if translation_texts is not None and len(translation_texts) > 0:
                return [{ "translation_text": translation_texts[0] }]
