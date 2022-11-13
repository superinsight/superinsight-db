import logging
import hashlib
import json
import requests
from environment import Environment
from common.model_types import ModelTypes
from api.ml.cacher import Cacher

class Predictor:

    logger = None
    db_database = None
    db_user = None

    def __init__(self, logger=None, handler = None, db_database = None, db_user = None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.logger.info("Init API.Predictor...")
      self.db_database = db_database
      self.db_user = db_user

    def __del__(self):
      self.logger.info("Exit API.Predictor...")

    def predict(self, model_name, sql, table_schema, table_name, table_column, limit=None):
      hash_object = hashlib.md5("{}_{}_{}_{}_{}".format(model_name, sql, table_schema, table_name, table_column).replace(" ","-").encode())
      cache_key = hash_object.hexdigest()
      cache_data = Cacher.get(cache_key)
      if cache_data is not None:
        data = json.loads(cache_data)
        return data["table_schema"], data["table_name"] 
      table_schema, table_name = self.__predict(model_name, sql, table_schema, table_name, table_column, limit)
      Cacher.set(cache_key, json.dumps({ "table_schema": table_schema, "table_name": table_name }))
      return table_schema, table_name

    def __predict(self, model_name, sql, table_schema, table_name, table_column, limit=None):
      if model_name.startswith(ModelTypes.SEMANTIC_SEARCH.value):
        similar = None
        return self.semanticSearch(sql = sql, similar=similar, table_schema=table_schema, table_name = table_name, table_column = table_column, limit=limit)
      elif model_name.startswith(ModelTypes.TEXT_CLASSIFICATION.value):
        return self.textClassification(sql = sql)
      elif model_name.startswith(ModelTypes.QUESTION_ANSWERING.value):
        question = None
        return self.questionAnswering(sql = sql, question=question)
      elif model_name.startswith(ModelTypes.SUMMARIZATION.value):
        return self.summarization(sql = sql)
      elif model_name.startswith(ModelTypes.TEXT_GENERATION.value):
        prompt = None
        min_length = 0
        max_length = 10 
        stop_word = None
        return self.textGeneration(sql = sql, prompt=prompt, min_length=min_length, max_length=max_length, stop_word=stop_word)
      elif model_name.startswith(ModelTypes.TRANSLATION.value):
        source_language = None
        target_language = None
        return self.translation(sql = sql, source_language = source_language, target_language = target_language)
      elif model_name.startswith(ModelTypes.RECOMMENDER.value):
        return self.recommender(sql = sql)
      else:
        return None, None
      
    def questionAnswering(self, sql, question):
      self.logger.info("API.Predictor.QuestionAnswering...")
      url = "{}/predict/{}/question-answering".format(Environment.host_mldb, self.db_database)
      self.logger.info("API.Predictor.QuestionAnswering:url:{}".format(url))
      payload = json.dumps({
        "inputs": [],
        "question": question,
        "sql": sql,
        "database_user": self.db_user
      })
      self.logger.info("API.Predictor.QuestionAnswering:payload:{}".format(payload))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      data = resp.json()
      self.logger.info("API.Predictor.QuestionAnswering:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.QuestionAnswering:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name

    def semanticSearch(self, sql, similar, table_schema, table_name, table_column, limit=None):
      self.logger.info("API.Predictor.SemanticSearch...")
      url = "{}/search/{}/{}/{}/{}".format(Environment.host_mldb, self.db_database, table_schema, table_name, table_column)
      self.logger.info("API.Predictor.SemanticSearch:url:{}".format(url))
      payload = json.dumps({
        "similar": similar,
        "sql": sql,
        "limit": limit,
        "database_user": self.db_user
      })
      self.logger.info("API.Predictor.SemanticSearch:payload:{}".format(payload))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      data = resp.json()
      self.logger.info("API.Predictor.SemanticSearch:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.SemanticSearch:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name


    def summarization(self, sql):
      self.logger.info("API.Predictor.Summarization...")
      url = "{}/predict/{}/summarization".format(Environment.host_mldb, self.db_database)
      self.logger.info("API.Predictor.Summarization:url:{}".format(url))
      payload = json.dumps({
        "inputs": [],
        "sql": sql,
        "database_user": self.db_user
      })
      self.logger.info("API.Predictor.Summarization:payload:{}".format(payload))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      data = resp.json()
      self.logger.info("API.Predictor.Summarization:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.Summarization:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name
        
    def textClassification(self, sql):
      self.logger.info("API.Predictor.TextClassification...")
      url = "{}/predict/{}/text-classification".format(Environment.host_mldb, self.db_database)
      self.logger.info("API.Predictor.TextClassification:url:{}".format(url))
      payload = json.dumps({
        "inputs": [],
        "labels": [],
        "sql": sql,
        "database_user": self.db_user
      })
      self.logger.info("API.Predictor.TextClassification:payload:{}".format(payload))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      data = resp.json()
      self.logger.info("API.Predictor.TextClassification:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.TextClassification:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name

    def textGeneration(self, sql ="", prompt = "", min_length = None, max_length=None, stop_word = None):
      self.logger.info("API.Predictor.TextGeneration...")
      url = "{}/predict/{}/text-generation".format(Environment.host_mldb, self.db_database)
      self.logger.info("API.Predictor.TextGeneration:url:{}".format(url))
      body ={
        "inputs": [],
        "sql": sql, 
        "prompt":  prompt,
        "min_length":  min_length,
        "max_length":  max_length,
        "stop_word": stop_word,
        "database_user": self.db_user
      } 
      self.logger.info("API.Predictor.TextGeneration:payload:{}".format(json.dumps(body)))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, json=body)
      data = resp.json()
      self.logger.info("API.Predictor.TextGeneration:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.TextGeneration:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name

    def translation(self, sql = "", source_language = None, target_language = None):
      self.logger.info("API.Predictor.Translation...")
      url = "{}/predict/{}/translation".format(Environment.host_mldb, self.db_database)
      self.logger.info("API.Predictor.Translation:url:{}".format(url))
      body ={
        "inputs": [],
        "sql": sql, 
        "source_language":  source_language,
        "target_language":  target_language,
        "database_user": self.db_user
      } 
      self.logger.info("API.Predictor.Translation:payload:{}".format(json.dumps(body)))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, json=body)
      data = resp.json()
      self.logger.info("API.Predictor.Translation:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.Translation:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name

    def recommender(self, sql):
      self.logger.info("API.Predictor.Recommender...")
      url = "{}/predict/{}/recommender".format(Environment.host_mldb, self.db_database)
      self.logger.info("API.Predictor.Recommender:url:{}".format(url))
      payload = json.dumps({
        "sql": sql,
        "database_user": self.db_user
      })
      self.logger.info("API.Predictor.Recommender:payload:{}".format(payload))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      data = resp.json()
      self.logger.info("API.Predictor.Recommender:data")
      self.logger.info(data)
      self.logger.info("API.Predictor.Recommender:return")
      table_schema = data["table_schema"]
      table_name = data["table_name"]
      return table_schema, table_name