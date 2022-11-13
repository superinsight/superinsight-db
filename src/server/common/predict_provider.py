from enum import Enum
from environment import Environment
class PredictProvider(Enum):
    SUPERINSIGHT= "SUPERINSIGHT"
    HUGGINGFACE = "HUGGINGFACE"

    def getDefault():
        if Environment.provider_inference_default == "SUPERINSIGHT":
            return PredictProvider.SUPERINSIGHT
        elif Environment.provider_inference_default == "HUGGINGFACE":
            return PredictProvider.HUGGINGFACE
        else:
            return None