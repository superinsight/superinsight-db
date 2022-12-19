from common.logger import CommonLogger
import uuid
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from environment import Environment
from common.predict_provider import PredictProvider
from ml.pipeline.summarization import SummarizationPipeline

model_name = Environment.default_model_summarization
pipeline = SummarizationPipeline(provider=PredictProvider.getDefault())


class Summarization:

    logger = None

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init ML.Predict.Summarization...")

    def __del__(self):
        self.logger.info("Exit ML.Predict.Summarization...")

    def predict(self, inputs, min_length=0, database=None, database_user=None):
        predict_id = uuid.uuid4().hex
        predictions = []
        min_cutback = 5
        inputs = [*set(inputs)]
        for input in inputs:
            predicted = pipeline.run(input, min_length=min_length)
            summary = predicted["summary_text"]
            if len(summary) + min_cutback > len(input):
                predictions.append((input, input))
            else:
                predictions.append((input, summary))
        sqlHelper = SqlHelper(database=database)
        (
            sql,
            table_schema,
            table_name,
        ) = SqlGenerator().scriptCreateSummarizationPredictOutputTable(
            predict_id=predict_id, database_user=database_user
        )
        sqlHelper.execute(sql)
        script_for_inserts = ""
        for predicted in predictions:
            input = predicted[0]
            summary = predicted[1]
            sql_insert = SqlGenerator().scriptInsertSummarizationPredictOutputTable(
                predict_id=predict_id, input=input, summary=summary
            )
            script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
        if script_for_inserts != "":
            sqlHelper.execute(script_for_inserts)
        return table_schema, table_name
