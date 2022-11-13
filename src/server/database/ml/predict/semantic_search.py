import logging
import json
import uuid
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
import hashlib
from environment import Environment
from cachetools import cached, TTLCache
import uuid
import requests

class SemanticSearch:

    logger = None
    cached_ttl = 10
    cache = TTLCache(maxsize=100, ttl=cached_ttl)

    def __init__(self, logger=None, handler = None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.logger.info("Init ML.Predict.SemanticSearch...")

    def __del__(self):
      self.logger.info("Exit ML.Predict.SemanticSearch...")

    def __cacheKey(self, database, table_schema, table_name, table_column, similar, primary_key_values, size):
      unique_id = "___{}___{}___{}___{}___{}___{}___{}___".format(database, table_schema, table_name, table_column, similar, primary_key_values, size)
      cache_key = hashlib.md5(unique_id.encode()).hexdigest()
      return cache_key
    
    def predict(self, similar = None, primary_key_values = None, size = 10000, database = None, table_schema = None, table_name = None, table_column = None, database_user = None):
      predict_id = uuid.uuid4().hex
      cache_key = self.__cacheKey(database = database, table_schema = table_schema, table_name = table_name, table_column = table_column, similar = similar, primary_key_values=primary_key_values, size = size)
      cache_data = self.cache.get(cache_key)
      if cache_data is not None:
        table_schema = cache_data[0]
        table_name = cache_data[1]
        return table_schema, table_name
      predicted = self.__search(database = database, table_schema = table_schema, table_name = table_name, table_column = table_column, similar = similar, primary_key_values=primary_key_values, size = size)
      predictions = predicted["predictions"]
      if predictions is not None:
        sqlHelper = SqlHelper(database = database)
        sql, table_schema, table_name = SqlGenerator().scriptCreateSemanticSearchOutputTable(predict_id=predict_id, database_user = database_user)
        self.logger.debug(sql)
        sqlHelper.execute(sql)
        script_for_inserts = ""
        unique_text = {}
        for predicted in predictions:
          if predicted is not None and predicted["text"] is not None and predicted["score"] is not None:
            text = predicted["text"]
            score = predicted["score"]
            hash_object = hashlib.md5(text.replace(" ","-").encode())
            key = hash_object.hexdigest()
            if key not in unique_text:
              sql_insert = SqlGenerator().scriptInsertSemanticSearchPredictOutputTable(predict_id=predict_id, similar = similar, input = text, score = score)
              script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
              unique_text[key] = text
        if script_for_inserts != "":
          sqlHelper.execute(script_for_inserts)
        self.logger.debug(unique_text)
        self.cache[cache_key] = (table_schema, table_name)
        return table_schema, table_name 
      else:
        return None, None
      
    def getIndexId(self, database, table_schema, table_name, table_column):
      index_id = hashlib.md5("{}_{}_{}_{}".format(database, table_schema, table_name, table_column).encode()).hexdigest()
      return index_id

    def __search(self, database, table_schema, table_name, table_column, similar, primary_key_values, size):
      if size is None or size == "None":
        size = 10000
      index_id = self.getIndexId(database, table_schema = table_schema, table_name = table_name , table_column = table_column)
      url = "{}/{}/{}/_search".format(Environment.provider_api_url_superinsight_search, database, index_id)
      self.logger.info("ML.Predict.SemanticSearch.__search:{}".format(url))
      payload = json.dumps({
        "size": size,
        "context": similar,
        "primary_key_values": primary_key_values,
      })
      self.logger.info("ML.Predict.SemanticSearch.__search:payload:{}".format(payload))
      response = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      predicted = response.json()
      return predicted