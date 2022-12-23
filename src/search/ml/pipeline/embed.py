from sentence_transformers import SentenceTransformer
from environment import Environment
import urllib.request
import shutil
import os
import torch
import hashlib
from torchvision import datasets, transforms
from torchvision.models import resnet152, ResNet152_Weights
from ml.pipeline.imageToText import ImageToTextPipeline
import numpy as np
from common.logger import CommonLogger
from common.helper import CommonHelper
from common.source_location import SourceLocation


class EmbedPipeline:

    context_embedding_dim = 1000
    text_embedding_dim = 512
    nlp_model = SentenceTransformer(Environment.semantic_search_model)
    vision_model = None
    logger = CommonLogger()

    def getVisionEncoder(self):
        self.logger.info("EmbedPipeline.getVisionEncoder")
        if self.vision_model is None:
            self.vision_model = resnet152(weights=ResNet152_Weights.DEFAULT)
            self.vision_model.eval()
        return self.vision_model

    def hasContextEmbedding(self, text):
        source_location = CommonHelper().get_source_location(text)
        return source_location is not None

    def encode(self, text):
        self.logger.info("EmbedPipeline.encode:", text)
        source_location = CommonHelper().get_source_location(text)
        if source_location is not None:
            (texts, labels) = ImageToTextPipeline().generate(text)
            text_generated = ""
            labels_generated = ""
            text_embedding = np.zeros(self.text_embedding_dim)
            label_embedding = np.zeros(self.text_embedding_dim)
            if len(texts) > 0:
                text_generated = ", ".join(texts)
                text_embedding = self.nlp_model.encode(text_generated)
            if len(labels) > 0:
                labels_generated = ", ".join(labels)
                label_embedding = self.nlp_model.encode(labels_generated)
            context_embedding = self.__encodeExternalImage(text)
            return (
                text_embedding,
                context_embedding,
                label_embedding,
                text_generated,
                labels_generated,
            )
        else:
            embedding = self.nlp_model.encode(text)
            return (embedding, np.zeros(self.context_embedding_dim), embedding, "", "")

    def __downloadImage(self, text):
        source_location = CommonHelper().get_source_location(text)
        if source_location == SourceLocation.URL:
            with urllib.request.urlopen(text) as response:
                info = response.info()
                if info.get_content_maintype() == "image":
                    image_dir = "/tmp/{}".format(hashlib.md5(text.encode()).hexdigest())
                    if os.path.isdir(image_dir) == True:
                        shutil.rmtree(image_dir)
                    os.makedirs(image_dir + "/0/")
                    image_path = (
                        image_dir + "/0/0." + info.get_content_subtype().lower()
                    )
                    with open(image_path, "wb") as localFile:
                        localFile.write(response.read())
            self.logger.info("EmbedPipeline.__downloadImage", text, image_dir)
            return image_dir
        return None

    def __encodeExternalImage(self, text):
        try:
            image_dir = self.__downloadImage(text)
            if image_dir is not None:
                return self.__getImageEmbeddings(image_dir)
            return np.zeros(self.context_embedding_dim)
        except Exception as e:
            self.logger.error(e)
            return np.zeros(self.context_embedding_dim)

    def __getImageEmbeddings(self, image_path):
        class ImageFolderWithPaths(datasets.ImageFolder):
            def __getitem__(self, index):
                return super(ImageFolderWithPaths, self).__getitem__(index) + (
                    self.imgs[index][0],
                )

        dataset = ImageFolderWithPaths(
            image_path,
            transform=transforms.Compose(
                [
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                    ),
                ]
            ),
        )
        dataloader = torch.utils.data.DataLoader(dataset, num_workers=0, batch_size=256)
        for (inputs, labels, paths) in dataloader:
            with torch.no_grad():
                embedding = self.getVisionEncoder()(inputs).squeeze().numpy()
                return embedding
        return None
