import uuid
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from common.predict_provider import PredictProvider
from ml.pipeline.question_answering import QuestionAnsweringPipeline
from common.logger import CommonLogger

pipeline = QuestionAnsweringPipeline(provider=PredictProvider.getDefault())


class QuestionAnswering:

    logger = None

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init ML.Predict.QuestionAnswering...")

    def __del__(self):
        self.logger.info("Exit ML.Predict.QuestionAnswering...")

    def predict(self, inputs, question, database=None, database_user=None):
        predict_id = uuid.uuid4().hex
        predictions = []
        inputs = [*set(inputs)]
        for input in inputs:
            output = pipeline.run(context=input, question=question)
            predictions.append((input, question, output))
        sqlHelper = SqlHelper(database=database)
        (
            sql,
            table_schema,
            table_name,
        ) = SqlGenerator().scriptCreateQuestionAnsweringPredictOutputTable(
            predict_id=predict_id, database_user=database_user
        )
        self.logger.debug(sql)
        sqlHelper.execute(sql)
        script_for_inserts = ""
        for predicted in predictions:
            if (
                predicted[0] is not None
                and predicted[1] is not None
                and predicted[2] is not None
            ):
                score = predicted[2]["score"]
                start = predicted[2]["start"]
                end = predicted[2]["end"]
                answer = predicted[2]["answer"]
                sql_insert = (
                    SqlGenerator().scriptInsertQuestionAnsweringPredictOutputTable(
                        predict_id=predict_id,
                        input=predicted[0],
                        question=predicted[1],
                        answer=answer,
                        score=score,
                        start=start,
                        end=end,
                    )
                )
                script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
        if script_for_inserts != "":
            sqlHelper.execute(script_for_inserts)
        return table_schema, table_name
