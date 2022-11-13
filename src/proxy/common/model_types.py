from enum import Enum

class ModelTypes(Enum):
    TEXT_CLASSIFICATION = "text_classification"
    QUESTION_ANSWERING = "question_answering"
    SEMANTIC_SEARCH = "semantic_search"
    SUMMARIZATION = "summarization"
    TEXT_GENERATION = "text_generation"
    TRANSLATION = "translation"
    RECOMMENDER = "recommender"

class ModelTypesValidation:
    
    def exists(model_type = None):
        if model_type.lower() == ModelTypes.TEXT_CLASSIFICATION.value:
            return True
        if model_type.lower() == ModelTypes.QUESTION_ANSWERING.value:
            return True
        if model_type.lower() == ModelTypes.SEMANTIC_SEARCH.value:
            return True
        if model_type.lower() == ModelTypes.SUMMARIZATION.value:
            return True
        if model_type.lower() == ModelTypes.TEXT_GENERATION.value:
            return True
        if model_type.lower() == ModelTypes.TRANSLATION.value:
            return True
        if model_type.lower() == ModelTypes.RECOMMENDER.value:
            return True
        return False

    def getList(prefix = ""):
        model_names = []
        model_names.append(prefix + ModelTypes.TEXT_CLASSIFICATION.value)
        model_names.append(prefix +ModelTypes.QUESTION_ANSWERING.value)
        model_names.append(prefix +ModelTypes.SEMANTIC_SEARCH.value)
        model_names.append(prefix +ModelTypes.SUMMARIZATION.value)
        model_names.append(prefix +ModelTypes.TEXT_GENERATION.value)
        model_names.append(prefix +ModelTypes.TRANSLATION.value)
        model_names.append(prefix +ModelTypes.RECOMMENDER.value)
        return model_names

