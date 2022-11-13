import torch
from storage.download import StorageDownload
from storage.model_types import ModelTypes
from transformers import AutoTokenizer, pipeline
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast 
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, ViTForImageClassification
from transformers import CLIPProcessor, CLIPModel
pipelines = {}
models = {}
tokenizers = {}
feature_extractor = {}
processor = {}

class StorageModel:

	logger = None
	pipeline = None

	def getPipeline(self, task, model_path, use_gpu=False):
		device = 0 if torch.cuda.is_available() and use_gpu else -1
		key = "{}_{}_{}".format(task, model_path, device)
		if pipelines.get(key) is None:
			model_pipeline = pipeline(task, model=model_path, device=device)
			pipelines[key] = model_pipeline
		return pipelines[key]

	def getModel(self, task = None, model_type = None, model_path = None, use_gpu=False):
		torch_device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
		key = "{}_{}_{}".format(task, model_path, torch_device)
		if models.get(key) is None:
			if self.isExtneralModelPath(model_path=model_path):
				model_path = StorageDownload().downloadModel(model_path)
			if model_type == str(ModelTypes.MBART.value):
				model = MBartForConditionalGeneration.from_pretrained(
					model_path).to(torch_device)
				models[key] = model
			if model_type == str(ModelTypes.VISION_ENCODER_DECODER.value):
				model = VisionEncoderDecoderModel.from_pretrained(model_path).to(torch_device)
				models[key] = model
			if model_type == str(ModelTypes.IMAGE_CLASSIFICATION.value):
				model = ViTForImageClassification.from_pretrained(model_path).to(torch_device)
				models[key] = model
			if model_type == str(ModelTypes.ZERO_SHOT_IMAGE_CLASSIFICATION.value):
				model = CLIPModel.from_pretrained(model_path).to(torch_device)
				models[key] = model

		return models[key]

	def getTokenizer(self, task = None, model_type = None, model_path = None, use_gpu=False):
		key = "{}_{}".format(task, model_path)
		if tokenizers.get(key) is None:
			if self.isExtneralModelPath(model_path=model_path):
				model_path = StorageDownload().downloadModel(model_path)
			if model_type == str(ModelTypes.MBART.value):
				tokenizers[key] = MBart50TokenizerFast.from_pretrained(model_path)
			else:
				tokenizers[key] = AutoTokenizer.from_pretrained(model_path)
		return tokenizers[key]

	def getFeatureExtractor(self, task = None, model_type = None, model_path = None, use_gpu=False):
		key = "{}_{}".format(task, model_path)
		if feature_extractor.get(key) is None:
			if self.isExtneralModelPath(model_path=model_path):
				model_path = StorageDownload().downloadModel(model_path)
			if model_type == str(ModelTypes.VISION_ENCODER_DECODER.value) or model_type == str(ModelTypes.IMAGE_CLASSIFICATION.value):
				feature_extractor[key] = ViTFeatureExtractor.from_pretrained(model_path)
		return feature_extractor[key]

	def getProcessor(self, task = None, model_type = None, model_path = None, use_gpu=False):
		key = "{}_{}".format(task, model_path)
		if processor.get(key) is None:
			if self.isExtneralModelPath(model_path=model_path):
				model_path = StorageDownload().downloadModel(model_path)
			if model_type == str(ModelTypes.ZERO_SHOT_IMAGE_CLASSIFICATION.value):
				processor[key] = CLIPProcessor.from_pretrained(model_path)
		return processor[key]

	def isExtneralModelPath(self, model_path):
		if model_path.startswith("gs://"):
			return True
		return False
     
