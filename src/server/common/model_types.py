from enum import Enum

class ModelTypes(Enum):
    TEXT_CLASSIFICATION = "text_classification"
    QUESTION_ANSWERING = "question_answering"
    SEMANTIC_SEARCH = "semantic_search"
    SUMMARIZATION = "summarization"
    TEXT_GENERATION = "text_generation"
    TRANSLATION = "translation"
    RECOMMENDER = "recommender"