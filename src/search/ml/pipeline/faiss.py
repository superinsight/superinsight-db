from cgitb import text
import logging
import pandas as pd
import numpy, copy, time
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from datasets import load_from_disk, Dataset
from scipy.special import softmax
from common.storage_location import StorageLocation
from ml.pipeline.embed import EmbedPipeline
import os
import pandas as pd
import os.path, json
from common.cacher import Cacher
from environment import Environment
import time, datetime
import faiss

class FaissPipeline:

    logger = None
    key = None
    storage = Environment.default_storage
    storage_location = None
    embed_pipeline = EmbedPipeline()
    dataframes = {}

    def __init__(self, logger=None, handler = None, max_records = None, storage_location = StorageLocation.MEMORY_CACHE):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      self.storage_location = storage_location
      if handler is not None:
        self.logger.addHandler(handler)
      self.logger.info("ml.pipeline.fass.__init__")
      if max_records is not None:
        self.max_records = max_records

    def __del__(self):
      self.logger.info("ml.pipeline.faiss.__del__")
      for key in self.dataframes:
        self.logger.info("ml.pipeline.fass.__del__:saving-dataframe-key:{}".format(key))
        cached_data = self.dataframes[key]
        self.logger.info(cached_data)
        df = pd.DataFrame.from_dict(cached_data[2])
        self.save(database=cached_data[0], index_id=cached_data[1], df = df)
      
    def __getEmptyDataset(self):
      return Dataset.from_dict({
          "_id" : [],
          "database" : [],
          "index_id" : [],
          "primary_key_name" : [],
          "primary_key_value" : [],
          "column_name" : [],
          "column_value" : [],
          "embedding":[],
          "context_embedding":[],
          "label_embedding":[],
          "text_generated":[],
          "labels_generated":[]
      })

    def __getDatasetFromCache(self, database, index_id):
      cache_key = "cache_faiss_{}_{}".format(database,index_id) 
      return Cacher.get(cache_key)

    def __getDataframeFromCache(self, database, index_id):
      cache_key = "cache_dataframe_{}_{}".format(database,index_id)
      if self.dataframes.get(cache_key) is not None and self.dataframes[cache_key][2] is not None:
        return pd.DataFrame.from_dict(self.dataframes[cache_key][2])
      return None

    def __getDatasetFromDisk(self, database, index_id):
      target_path = "{}/{}/{}".format(self.storage, database, index_id)
      if os.path.exists(target_path):
        self.logger.info("__getDatasetFromDisk: {} for database: {} index_id: {}".format(target_path, database, index_id))
        return load_from_disk(target_path)
      else:
        return None

    def __setDatasetToCache(self, database, index_id, ds):
      cache_key = "cache_faiss_{}_{}".format(database,index_id) 
      self.logger.info("Caching embedding count: {} for database: {} index_id: {}".format(ds.num_rows, database, index_id))
      Cacher.set(key=cache_key, value=ds)

    def __setDataframeToCache(self, database, index_id, df):
      cache_key = "cache_dataframe_{}_{}".format(database,index_id) 
      self.logger.info("Caching dataframe cache_key: {} for database: {} index_id: {}".format(cache_key, database, index_id))
      self.dataframes[cache_key] = (database, index_id, df.to_dict())

    def __saveDatasetToDisk(self, database, index_id, ds):
      target_path = "{}/{}/{}".format(self.storage, database, index_id)
      self.logger.info("Saving with embedding count: {} for database: {} index_id: {} to path: {}".format(ds.num_rows, database, index_id, target_path))
      ds.save_to_disk(target_path)

    def __dropDataframeRow(self, df, column_name, column_value):
      if df.empty is False:
        if is_string_dtype(df[column_name]):
          df.drop(df.index[df[column_name] == str(column_value)], inplace=True)
        if is_numeric_dtype(df[column_name]):
          df.drop(df.index[df[column_name] == int(column_value)], inplace=True)

    def __validate(self, items):
      key = None
      for item in items:
        index_id = item["index_id"]
        if key is None:
          key = index_id
        else:
          if key != index_id:
              error_message = "Items in dataset has more than one index:{}".format(json.dumps(items))
              self.logger.error(error_message)
              raise Exception(error_message)
      return True

    def get(self, database, index_id):
      ds = None
      if self.storage_location == StorageLocation.MEMORY_CACHE:
        ds = self.__getDatasetFromCache(database=database, index_id=index_id)
      if self.storage_location == StorageLocation.LOCAL_DISK:
        ds = self.__getDatasetFromDisk(database=database, index_id=index_id)
      if ds is not None:
        return ds
      else:
        return self.__getEmptyDataset() 
        
    def write(self, database, index_id, items):
      records = copy.deepcopy(items)
      start_time = time.time()
      self.__validate(records)
      df = self.__getDataframeFromCache(database=database, index_id=index_id)
      self.logger.info("ml.pipeline.faiss-get-dataframe-from-cache-in-{}-seconds-during-{}".format(time.time() - start_time,datetime.datetime.now()))
      if df is None:
        ds = self.get(database=database, index_id=index_id)
        df = pd.DataFrame(ds)
        self.logger.info("ml.pipeline.faiss-get-dataframe-from-dataset-on-disk-in-{}-seconds-during-{}".format(time.time() - start_time,datetime.datetime.now()))
      for record in records:
        if record.get("embedding") is not None:
          record["embedding"] = numpy.array(json.loads(record["embedding"]))
        if record.get("context_embedding") is not None:
          record["context_embedding"] = numpy.array(json.loads(record["context_embedding"]))
        if record.get("label_embedding") is not None:
          record["label_embedding"] = numpy.array(json.loads(record["label_embedding"]))
        df_item = pd.DataFrame([record])
        if df_item is not None and record["operation"]== "DELETE":
          self.__dropDataframeRow(df = df, column_name=record["primary_key_name"], column_value=record["primary_key_value"])
        elif record["operation"]== "INSERT":
          df = pd.concat([df, df_item], ignore_index=True)
          df = df.drop_duplicates(subset=["database","index_id","_id"], keep='last')
          df = df.drop_duplicates(subset=["database","index_id","operation", "primary_key_name","primary_key_value"], keep='last')
      self.__setDataframeToCache(database=database, index_id=index_id, df=df) 
      self.logger.info("ml.pipeline.faiss-updated-dataset-in-{}-seconds-during-{}".format(time.time() - start_time,datetime.datetime.now()))
      self.save(database=database, index_id=index_id, df=df) 
      self.logger.info("ml.pipeline.faiss-completed-in-{}-seconds-during-{}".format(time.time() - start_time,datetime.datetime.now()))
      return df
      
    def save(self, database, index_id, df = None):
      if df is not None:
        ds = Dataset.from_pandas(df, preserve_index=False)
        if ds is not None and self.storage_location == StorageLocation.MEMORY_CACHE:
          self.__setDatasetToCache(database=database, index_id=index_id, ds=ds)
        if ds is not None and self.storage_location == StorageLocation.LOCAL_DISK:
          self.__saveDatasetToDisk(database=database, index_id=index_id, ds=ds)

    def count(self, database, index_id):
      ds = self.get(database=database, index_id=index_id)
      return ds.num_rows

    def __getSamplesForText(self, ds, embedding, limit):
      predictions = []
      ds.add_faiss_index(column="embedding", metric_type= faiss.METRIC_INNER_PRODUCT)
      scores, samples = ds.get_nearest_examples("embedding", embedding, k=limit)
      samples_df = pd.DataFrame.from_dict(samples)
      samples_df["scores"] = scores
      samples_df.sort_values("scores", ascending=False, inplace=True)
      for _, row in samples_df.iterrows():
          prediction = {"id": row.primary_key_value, "text": row.column_value, "score": min(row.scores, 1.00)}
          if hasattr(row,"text_generated"):
            prediction["label"] = row.text_generated 
          predictions.append(prediction)
      return predictions

    def __getSamplesForLabel(self, ds, label_embedding, limit):
      predictions = []
      ds.add_faiss_index(column="label_embedding", metric_type= faiss.METRIC_INNER_PRODUCT)
      scores, samples = ds.get_nearest_examples("label_embedding", label_embedding, k=limit)
      samples_df = pd.DataFrame.from_dict(samples)
      samples_df["scores"] = scores
      samples_df.sort_values("scores", ascending=False, inplace=True)
      for _, row in samples_df.iterrows():
          prediction = {"id": row.primary_key_value, "text": row.column_value, "score": min(row.scores, 1.00)}
          if hasattr(row,"labels_generated"):
            prediction["label"] = row.labels_generated 
          predictions.append(prediction)
      return predictions
    
    def __getSamplesForImages(self, ds, context_embedding, limit):
      predictions = []
      ds.add_faiss_index(column="context_embedding", metric_type= faiss.METRIC_L2)
      scores, samples = ds.get_nearest_examples("context_embedding", context_embedding, k=limit)
      samples_df = pd.DataFrame.from_dict(samples)
      max_score = len(context_embedding)
      weighted_scores = []
      for score in scores:
        weighted_scores.append((max_score - score) / max_score)
      samples_df["scores"] = numpy.array(weighted_scores)
      samples_df.sort_values("scores", ascending=False, inplace=True)
      for _, row in samples_df.iterrows():
          prediction = {"id": row.primary_key_value, "text": row.column_value, "score": row.scores}
          predictions.append(prediction)
      return predictions
    
    def search(self, database, index_id, context, limit = 10, primary_key_values= None):
      predictions = []
      ds = self.get(database=database, index_id=index_id)
      if ds is None or ds.num_rows == 0:
        return predictions
      if primary_key_values is not None and primary_key_values != "None":
        try:
          ids =json.loads(primary_key_values.replace("'","\""))
          ds = ds.filter(lambda x: x["primary_key_value"] in ids)
        except:
          self.logger.error("Error in parsing out primary_key_values".format(primary_key_values))
      text_embedding, context_embedding, label_embedding, text_generated, labels_generated = self.embed_pipeline.encode(context)
      has_context_embedding = self.embed_pipeline.hasContextEmbedding(context)
      if has_context_embedding is True:
        return self.__getSamplesForImages(ds = ds, context_embedding = context_embedding, limit = limit)
      if text_embedding is not None:
        text_predictions =  self.__getSamplesForText(ds = ds, embedding = text_embedding, limit = limit)
        predictions = predictions + text_predictions
      if label_embedding is not None:
        label_predictions =  self.__getSamplesForLabel(ds = ds, label_embedding = label_embedding, limit = limit)
        predictions = predictions + label_predictions
      predictions.sort(key=lambda x: x["score"], reverse=True)
      dict_predictions = {}
      for element in predictions:
        key = element["id"]
        if dict_predictions.get(key) is None:
          dict_predictions[key] = element
      return [i for i in dict_predictions.values()]