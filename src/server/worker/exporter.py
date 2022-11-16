import logging
from environment import Environment
from database.sql.table_logger import TableLogger
from common.storage_location import StorageLocation
from common.export_destination import ExportDestination 
from database.ml.predict.semantic_search import SemanticSearch
import requests
from kafka import KafkaProducer
import json

class Exporter:

  logger = None
  app_instance_id = None
  version = None
  database = None
  destination = None 
  producer = None

  def __init__(self, logger = None, handler = None, instance_id = None, database = None, version = None, destination = ExportDestination.HTTP):
    self.logger = logger or logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    if handler is not None:
      self.logger.addHandler(handler)
    self.instance_id = instance_id
    self.database = database 
    self.version = version
    self.destination = destination
    if self.destination == ExportDestination.STREAMING:
      self.producer = KafkaProducer(bootstrap_servers=Environment.kafka_bootstrap_servers, key_serializer=str.encode, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    self.logger.info("Init Exporter for instance: {}".format(self.instance_id))

  def __del__(self):
    self.logger.info("Exit Exporter...")

  def exportTableLogs(self, table_schema, table_name, column_name, rows, version):
    if self.destination == ExportDestination.HTTP:
      self.post(database=self.database, table_schema=table_schema, table_name=table_name, table_column=column_name, rows = rows, version= version)
    if self.destination == ExportDestination.STREAMING:
      self.produce(database=self.database, table_schema=table_schema, table_name=table_name, table_column=column_name, rows = rows, version= version)

  def verifyDestination(self):
    if self.destination == ExportDestination.HTTP:
      try:
        http_resp = requests.get(Environment.provider_api_url_superinsight_search_indexing)
        return http_resp.status_code == 200
      except:
        return False
    elif self.destination == ExportDestination.STREAMING:
      return True
    else:
      return False

  def exportTableLogger(self):
    if self.verifyDestination() == False:
      return
    table_logger = TableLogger(database = self.database)
    tables = table_logger.readRecentUpdates(primary_key_name = StorageLocation.LOCAL_DISK.value, primary_key_value = self.instance_id, version_after_id = self.version)
    if tables is not None and len(tables) > 0:
      version = tables[0]["version"]
      table_logger.insertTableLog(last_row_id= version, operation = "INDEXING", primary_key_name = StorageLocation.LOCAL_DISK.value, primary_key_value = self.instance_id)
      for table in tables:
        self.exportTableLogs(table_schema = table["table_schema"], table_name = table["table_name"], column_name = table["column_name"], rows = table["rows"], version= version)
      table_logger.insertTableLog(last_row_id = version, operation = "INDEXED", primary_key_name = StorageLocation.LOCAL_DISK.value, primary_key_value = self.instance_id)
      self.version = version

  def post(self, database, table_schema, table_name, table_column, rows, version):
    index_id = SemanticSearch().getIndexId(database= database, table_schema = table_schema, table_name = table_name , table_column = table_column)
    url = "{}/{}/{}/".format(Environment.provider_api_url_superinsight_search_indexing, database, index_id)
    messages = self.formatForHttpPost(database =database, index_id = index_id, table_column = table_column, rows=rows)
    payload = json.dumps({ "items": messages })
    self.logger.info("Export Messsges via HTTP POST: {}".format(payload))
    response = requests.request("POST", url, headers={ "accept": "application/json", "Content-Type": "application/json" }, data=payload)
    self.logger.info("Export Messsges via HTTP RESPONSE: {}".format(response.json()))
  
  def produce(self, database, table_schema, table_name, table_column, rows, version):
    index_id = SemanticSearch().getIndexId(database= database, table_schema = table_schema, table_name = table_name , table_column = table_column)
    messages = self.formatForStreaming(database =database, index_id = index_id, table_column = table_column, rows=rows)
    for message in messages:
      future = self.producer.send(Environment.kafka_topic_ml_search, key=index_id, value=message)
      future.get(timeout=60)
    self.producer.flush()

  def formatForStreaming(self, database, index_id, table_column, rows):
    messages = []
    max_message_size = 100000
    batch = {}
    for row in rows:
      _id = row["_id"]
      if row.get("column_value") is not None and len(row["column_value"]) == 0:
        continue
      batch[_id] = {
        "_id": _id,
        "database": database,
        "index_id": index_id,
        "primary_key_name": row["primary_key_name"],
        "primary_key_value": row["primary_key_value"],
        "column_name": table_column,
        "column_value": row["column_value"],
        "operation": row["operation"],
        "created_on": row["created_on"]
      }
      message_size = len(json.dumps(batch).encode('utf-8'))
      if message_size > max_message_size:
        messages.append(list(batch.values()))
        batch = {}
    messages.append(list(batch.values()))
    return messages

  def formatForHttpPost(self, database, index_id, table_column, rows):
    messages = []
    for row in rows:
      _id = row["_id"]
      if row.get("column_value") is not None and len(row["column_value"]) == 0:
        continue
      messages.append({
        "_id": _id,
        "database": database,
        "index_id": index_id,
        "primary_key_name": row["primary_key_name"],
        "primary_key_value": row["primary_key_value"],
        "column_name": table_column,
        "column_value": row["column_value"],
        "operation": row["operation"],
        "created_on": row["created_on"]
      })
    return messages