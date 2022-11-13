import logging
import uuid
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from common.predict_provider import PredictProvider
from ml.pipeline.translation import TranslationPipeline
pipeline = TranslationPipeline(provider = PredictProvider.getDefault())

class Translation:

    logger = None


    def __init__(self, logger=None, handler = None):
      self.logger = logger or logging.getLogger(__name__)
      self.logger.setLevel(logging.INFO)
      if handler is not None:
        self.logger.addHandler(handler)
      self.logger.info("Init ML.Predict.Translation...")

    def __del__(self):
      self.logger.info("Exit ML.Predict.Translation...")

    def predict(self, inputs, source_language, target_language, database=None, database_user = None):
      predict_id = uuid.uuid4().hex
      predictions = []
      inputs = [*set(inputs)]
      for input in inputs:
        translation = input
        if source_language != target_language:
          translation = pipeline.run(input = input, src_lang = source_language, tgt_lang = target_language)
          predictions.append((input, translation))
      sqlHelper = SqlHelper(database=database)
      sql, table_schema, table_name = SqlGenerator().scriptCreateTranslationPredictOutputTable(predict_id=predict_id, database_user=database_user)
      sqlHelper.execute(sql)
      script_for_inserts = ""
      for predicted in predictions:
        input = predicted[0]
        translation = predicted[1]
        sql_insert = SqlGenerator().scriptInsertTranslationPredictOutputTable(predict_id=predict_id, input=input, source_language = source_language, target_language = target_language, output=translation)
        script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
      if script_for_inserts != "":
        sqlHelper.execute(script_for_inserts)
      return table_schema, table_name 