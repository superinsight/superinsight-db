import logging
import hashlib
import json
import requests
from environment import Environment
from common.model_types import ModelTypes
from api.ml.cacher import Cacher

class Trainer:

    logger = None
    db_database = None
    db_user = None

    def __init__(self, logger=None, handler = None, db_database = None, db_user = None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.logger.info("Init API.ML.Trainer...")
      self.db_database = db_database
      self.db_user = db_user

    def __del__(self):
      self.logger.info("Exit API.ML.Trainer...")

    def train(self, model_name, model_type, training_data):
      model_id = self.__train(model_name, model_type, training_data)
      return model_id

    def __train(self, model_name, model_type, training_data):
      self.logger.info("API.ML.Trainer.__train...")
      hash_object = hashlib.md5("{}_{}_{}".format(self.db_database, model_type, model_name).replace(" ","-").encode())
      model_id = hash_object.hexdigest()
      url = "{}/train/{}/{}".format(Environment.host_mldb, self.db_database, model_type)
      self.logger.info("API.ML.Trainer.__train:url:{}".format(url))
      payload = json.dumps({
        "model_id": model_id,
        "sql": training_data,
        "database_user": self.db_user
      })
      self.logger.info("API.ML.Trainer.__train:payload:{}".format(payload))
      resp = requests.request("POST", url, headers = { "Content-Type": "application/json"}, data=payload)
      data = resp.json()
      self.logger.info("API.ML.Trainer.__train:data")
      self.logger.info(data)
      self.logger.info("API.ML.Trainer.__train:return")
      return model_id