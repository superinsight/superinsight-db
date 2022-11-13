from enum import Enum

class ModelTypes(Enum):
    MBART = "mbart"
    VISION_ENCODER_DECODER = "vision_encoder_decoder"
    IMAGE_CLASSIFICATION = "image_classification"
    ZERO_SHOT_IMAGE_CLASSIFICATION = "zero_shot_image_classification"