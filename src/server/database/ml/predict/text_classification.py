from common.logger import CommonLogger
import uuid
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from common.predict_provider import PredictProvider
from ml.pipeline.text_classification import TextClassificationPipeline


class TextClassification:

    logger = None

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init ML.Predict.TextClassification...")

    def __del__(self):
        self.logger.info("Exit ML.Predict.TextClassification...")

    def predict(self, inputs, labels, database=None, database_user=None):
        predict_id = uuid.uuid4().hex
        pipeline = TextClassificationPipeline(provider=PredictProvider.getDefault())
        inputs = [*set(inputs)]
        predictions = []
        for input in inputs:
            output = pipeline.run(inputs=input, labels=labels)
            predictions.append(output)
        sqlHelper = SqlHelper(database=database)
        (
            sql,
            table_schema,
            table_name,
        ) = SqlGenerator().scriptCreateTextClassificationPredictOutputTable(
            predict_id=predict_id, labels=labels, database_user=database_user
        )
        sqlHelper.execute(sql)
        script_for_inserts = ""
        for predicted in predictions:
            text = predicted["sequence"]
            params = []
            for x in range(len(predicted["labels"])):
                params.append((predicted["labels"][x], predicted["scores"][x]))
            sql_insert = SqlGenerator().scriptInsertTextPredictOutputTable(
                predict_id=predict_id, text=text, params=params
            )
            script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
        if script_for_inserts != "":
            sqlHelper.execute(script_for_inserts)
        return table_schema, table_name
