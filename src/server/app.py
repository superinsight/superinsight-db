import os, asyncio, uuid
from database.sql.helper import SqlHelper
from database.sql.rewriter import SqlRewriter
from database.ml.train.recommender import TrainRecommender
from common.model_types import ModelTypes
from database.sql.query_parser import QueryParser
from environment import Environment
from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI()

from database.ml.predict.text_classification import TextClassification
from database.ml.predict.question_answering import QuestionAnswering 
from database.ml.predict.summarization import Summarization
from database.ml.predict.text_generation import TextGeneration
from database.ml.predict.translation import Translation
from database.ml.predict.recommender import Recommender
from database.ml.predict.semantic_search import SemanticSearch

version = "0.9.1"
os.environ['KMP_DUPLICATE_LIB_OK']='True'

@app.on_event("startup")
async def startup_event():
    print("app startup continues....")

@app.get("/")
async def HealthCheck():
    return {"version": version}

class PredictRequest(BaseModel):
    inputs: list = []
    labels: list = []
    question: str = None
    prompt: str = None
    similar: str= None
    min_length: int = None
    max_length: int = None
    stop_word: str = None
    source_language: str = None
    target_language: str = None
    sql: str = None
    database_user: str
    limit: int = None

class TrainRequest(BaseModel):
    sql: str
    database_user: str
    model_id: str = None

@app.post("/predict/{database}/question-answering")
async def predict_Question_Answering(database: str, predict_request: PredictRequest):
    inputs = predict_request.inputs
    question = predict_request.question
    if predict_request.sql is not None:
        rewriter = SqlRewriter(sql = predict_request.sql)
        sql = rewriter.removeWhereCondition(full_table_name="predictions")
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.QUESTION_ANSWERING.value, table_column="question")
        if values is not None:
            question = values
        sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.QUESTION_ANSWERING.value, sql = sql)
        rows = SqlHelper(database = database).read(sql)
        inputs = [row[0] for row in rows]
    table_schema, table_name  = QuestionAnswering().predict(inputs = inputs, question = question, database = database, database_user = predict_request.database_user)
    return {"table_schema": table_schema, "table_name": table_name }

@app.post("/predict/{database}/recommender")
async def predict_Recommender(database: str, predict_request: PredictRequest):
    inputs = []
    table_schema = None
    table_name = None
    if predict_request.sql is not None:
        model_id = QueryParser(sql=predict_request.sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.RECOMMENDER.value, table_column="model_id")
        max_size = QueryParser(sql=predict_request.sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.RECOMMENDER.value, table_column="max_size")
        if model_id is not None:
            rewriter = SqlRewriter(sql = predict_request.sql)
            sql = rewriter.removeWhereCondition(full_table_name="predictions")
            sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.RECOMMENDER.value, sql = sql)
            rows = SqlHelper(database = database).read(sql)
            inputs = [row[0] for row in rows]
            table_schema, table_name  = Recommender().predict(inputs = inputs, database = database, model_id = model_id, database_user = predict_request.database_user, size = max_size)
    return {"table_schema": table_schema, "table_name": table_name }
   
@app.post("/predict/{database}/summarization")
async def predictSummarization(database: str, predict_request: PredictRequest):
    inputs = predict_request.inputs
    min_length = 0
    if predict_request.min_length is not None:
        min_length = predict_request.min_length
    if predict_request.sql is not None:
        rewriter = SqlRewriter(sql = predict_request.sql)
        sql = rewriter.removeWhereCondition(full_table_name="predictions")
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.SUMMARIZATION.value, table_column="min_length")
        if values is not None:
            min_length = int(values)
        sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.SUMMARIZATION.value, sql = sql)
        rows = SqlHelper(database = database).read(sql)
        inputs = [row[0] for row in rows]
    table_schema, table_name  = Summarization().predict(inputs = inputs, min_length = min_length, database = database, database_user = predict_request.database_user)
    return {"table_schema": table_schema, "table_name": table_name }
    
@app.post("/predict/{database}/text-classification")
async def predict_Text_Classification(database: str, predict_request: PredictRequest):
    inputs = predict_request.inputs
    labels = predict_request.labels
    if predict_request.sql is not None:
        rewriter = SqlRewriter(sql = predict_request.sql)
        sql = rewriter.removeWhereCondition(full_table_name="predictions")
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TEXT_CLASSIFICATION.value, table_column="labels")
        if values is not None:
            labels = values.split(',')
        sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.TEXT_CLASSIFICATION.value, sql = sql)
        rows = SqlHelper(database = database).read(sql)
        inputs = [row[0] for row in rows]
    table_schema, table_name  = TextClassification().predict(inputs = inputs, labels = labels, database = database, database_user = predict_request.database_user)
    return {"table_schema": table_schema, "table_name": table_name }

@app.post("/predict/{database}/text-generation")
async def predict_Text_Generation(database: str, predict_request: PredictRequest):
    inputs = predict_request.inputs
    prompt = predict_request.prompt
    min_length = predict_request.min_length
    max_length = predict_request.max_length
    stop_word = None
    if predict_request.stop_word is not None:
        stop_word = predict_request.stop_word
    if predict_request.sql is not None:
        rewriter = SqlRewriter(sql = predict_request.sql)
        sql = rewriter.removeWhereCondition(full_table_name="predictions")
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TEXT_GENERATION.value, table_column="inputs")
        if values is not None:
            inputs = values
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TEXT_GENERATION.value, table_column="prompt")
        if values is not None:
            prompt = values
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TEXT_GENERATION.value, table_column="min_length")
        if values is not None:
            min_length = int(values)
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TEXT_GENERATION.value, table_column="max_length")
        if values is not None:
            max_length = int(values)
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TEXT_GENERATION.value, table_column="stop_word")
        if values is not None:
            stop_word = values
        sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.TEXT_GENERATION.value, sql = sql)
        rows = SqlHelper(database = database).read(sql)
        inputs = [row[0] for row in rows]
    table_schema, table_name  = TextGeneration().predict(inputs = inputs, stop_word = stop_word, max_length = max_length, min_length = min_length, prompt=prompt, database = database, database_user = predict_request.database_user)
    return {"table_schema": table_schema, "table_name": table_name }

@app.post("/predict/{database}/translation")
async def predict_Translation(database: str, predict_request: PredictRequest):
    inputs = predict_request.inputs
    source_language = predict_request.source_language
    target_language = predict_request.target_language
    if predict_request.sql is not None:
        rewriter = SqlRewriter(sql = predict_request.sql)
        sql = rewriter.removeWhereCondition(full_table_name="predictions")
        source_values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TRANSLATION.value, table_column="source_language")
        target_values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.TRANSLATION.value, table_column="target_language")
        if source_values is not None:
            source_language = source_values
        if target_values is not None:
            target_language = target_values
        sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.TRANSLATION.value, sql = sql)
        rows = SqlHelper(database = database).read(sql)
        inputs = [row[0] for row in rows]
    table_schema, table_name  = Translation().predict(inputs = inputs, source_language = source_language, target_language = target_language, database = database, database_user = predict_request.database_user)
    return {"table_schema": table_schema, "table_name": table_name }

@app.post("/search/{database}/{table_schema}/{table_name}/{table_column}")
async def predict_Search(database: str, table_schema: str, table_name: str, table_column: str, predict_request: PredictRequest):
    sql = predict_request.sql
    similar = predict_request.similar
    limit = predict_request.limit
    primary_key_values = None
    if sql is not None:
        rewriter = SqlRewriter(sql = sql)
        sql = rewriter.removeWhereCondition(full_table_name="predictions")
        values = QueryParser(sql=sql).getWhereValues(table_schema=Environment.model_schema_name, table_name=ModelTypes.SEMANTIC_SEARCH.value, table_column="similar")
        if values is not None:
            similar = values
        else:
            similar ="*"
        sql = rewriter.removeWhereCondition(full_table_name=ModelTypes.SEMANTIC_SEARCH.value, sql = sql)
        similar, primary_key_values = rewriter.alterToSemanticSearchQuery(database = database, sql = sql, similar = similar)
    table_schema, table_name  = SemanticSearch().predict(similar=similar, primary_key_values = primary_key_values, size=limit, table_schema = table_schema, table_name=table_name, table_column=table_column, database = database, database_user = predict_request.database_user)
    return {"table_schema": table_schema, "table_name": table_name }

@app.post("/train/{database}/recommender")
async def train_Recommender(database: str, train_request: TrainRequest):
    model_id = train_request.model_id
    if train_request.sql is not None:
        model_id = TrainRecommender(database=database).initialize(sql=train_request.sql, model_id=train_request.model_id)
    return  {"model_id": model_id }