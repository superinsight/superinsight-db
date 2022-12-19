from common.logger import CommonLogger
import uuid, codecs
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from common.predict_provider import PredictProvider
from ml.pipeline.text_generation import TextGenerationPipeline

pipeline = TextGenerationPipeline(provider=PredictProvider.getDefault())


class TextGeneration:

    logger = None

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init ML.Predict.TextGeneration...")

    def __del__(self):
        self.logger.info("Exit ML.Predict.TextGeneration...")

    def predict(
        self,
        inputs,
        max_length=10,
        min_length=0,
        stop_word=None,
        prompt="",
        database=None,
        database_user=None,
    ):
        predict_id = uuid.uuid4().hex
        predictions = []
        inputs = [*set(inputs)]
        for input in inputs:
            input_prompt = "{}{}".format(input, prompt)
            generated_texts = pipeline.run(
                prompt=input_prompt, min_length=min_length, max_length=max_length
            )
            self.logger.debug(generated_texts)
            output = ""
            if (
                generated_texts is not None
                and len(generated_texts) > 0
                and generated_texts[0].get("generated_text") is not None
            ):
                output = generated_texts[0]["generated_text"].replace(
                    input_prompt, "", 1
                )
            if stop_word is not None:
                output = output.split(
                    str(codecs.escape_decode(stop_word)[0].decode("utf-8"))
                )[0]
            predictions.append((input, prompt, output))
        sqlHelper = SqlHelper(database=database)
        (
            sql,
            table_schema,
            table_name,
        ) = SqlGenerator().scriptCreateTextGenerationPredictOutputTable(
            predict_id=predict_id, database_user=database_user
        )
        sqlHelper.execute(sql)
        script_for_inserts = ""
        for predicted in predictions:
            input = predicted[0]
            prompt = predicted[1]
            output = predicted[2]
            sql_insert = SqlGenerator().scriptInsertTextGenerationPredictOutputTable(
                predict_id=predict_id, input=input, prompt=prompt, output=output
            )
            script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
        if script_for_inserts != "":
            sqlHelper.execute(script_for_inserts)
        return table_schema, table_name
