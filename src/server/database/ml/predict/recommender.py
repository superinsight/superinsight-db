import uuid
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from environment import Environment
from cachetools import cached, TTLCache
import uuid
import json
import requests
from common.logger import CommonLogger


class Recommender:

    logger = None
    one_min = 60
    cache = TTLCache(maxsize=100, ttl=one_min)

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init ML.Predict.Recommender...")

    def __del__(self):
        self.logger.info("Exit ML.Predict.Recommender...")

    def predict(
        self, inputs, size=10, model_id=None, database=None, database_user=None
    ):
        predict_id = uuid.uuid4().hex
        predictions = []
        if size is None or size.isnumeric() == False:
            size = 3
        inputs = [*set(inputs)]
        for input in inputs:
            predicted = self.http_request(database, model_id, input, size)
            user_predictions = predicted["predictions"]
            for recommended_item in user_predictions:
                predictions.append(
                    (input, recommended_item["item_id"], recommended_item["score"])
                )
        sqlHelper = SqlHelper(database=database)
        (
            sql,
            table_schema,
            table_name,
        ) = SqlGenerator().scriptCreateRecommenderPredictOutputTable(
            predict_id=predict_id, database_user=database_user
        )
        sqlHelper.execute(sql)
        script_for_inserts = ""
        for predicted in predictions:
            user_id = str(predicted[0])
            item_id = str(predicted[1])
            score = float(predicted[2])
            sql_insert = SqlGenerator().scriptInsertRecommenderPredictOutputTable(
                predict_id=predict_id, user_id=user_id, item_id=item_id, score=score
            )
            script_for_inserts = "{}\n{}".format(script_for_inserts, sql_insert)
        if script_for_inserts != "":
            sqlHelper.execute(script_for_inserts)
        return table_schema, table_name

    def http_request(self, database, model_id, input, size):
        cache_key = self.__cacheKey(database, model_id, input, size)
        if self.cache.get(cache_key) is None:
            url = "{}/{}/{}/user/{}?size={}".format(
                Environment.provider_api_url_superinsight_recommender,
                database,
                model_id,
                input,
                size,
            )
            response = requests.request("GET", url, headers={}, data={})
            predicted = response.json()
            self.cache[cache_key] = json.dumps(predicted)
            return predicted
        else:
            return json.loads(self.cache[cache_key])

    def __cacheKey(self, database, model_id, input, size):
        return "___{}___{}___{}___{}___".format(database, model_id, input, size)
