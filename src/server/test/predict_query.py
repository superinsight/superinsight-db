import unittest
from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator


class TestPredictQuery(unittest.TestCase):

    SQL_PREDICT_TEXT_CLASSIFICATION = "SELECT * FROM mldb.movie as movie JOIN model.text_classification as m on m.inputs = movie.overview JOIN model.text_classification as m on m.labels = ['drama,comedy'] WHERE mldb.movie._id = 2"
    SQL_PREDICT_TEXT_CLASSIFICATION_INPUT_QUERY = (
        "SELECT overview from mldb.movie WHERE mldb.movie._id = 2"
    )
    SQL_PREDICT_QUESTION_ANSWERING = "SELECT * FROM mldb.movie as movie JOIN model.question_answering m on m.inputs = movie.overview JOIN model.question_answering as m on m.question = ['Who is the main character of the movie'] WHERE movie._id = 8;"
    SQL_PREDICT_TEXT_GENERATION = "SELECT movie._id, movie.title, predictions.* FROM mldb.movie as movie JOIN model.text_generation m on m.inputs = movie.overview JOIN model.text_generation as m on m.stop_word = ['bull'] JOIN model.text_generation m on m.prompt = [' What type of audience will like movie? This movie is best for people who like'] WHERE mldb.movie._id = 12"
    SQL_SEARCH_IN_CLAUSE = "SELECT mldb.movie._id, mldb.movie.title, mldb.movie.overview, predictions.score FROM mldb.movie JOIN model.semantic_search ON model.semantic_search.inputs = mldb.movie.overview WHERE mldb.movie.id in (1,2) AND model.semantic_search.similar = 'gangster' ORDER BY predictions.score DESC"

    def test_search_with_in_clause(self):
        parser = QueryParser(self.SQL_SEARCH_IN_CLAUSE)
        (
            input_query,
            model_name,
            input_schema,
            input_table,
            input_column,
            input_values,
            limit,
            order_by,
        ) = parser.getPredictParams()

        self.assertEqual(
            input_query,
            "SELECT overview from mldb.movie WHERE mldb.movie.id in (1,2) AND model.semantic_search.similar = 'gangster'",
        )
        self.assertEqual(order_by, ["predictions.score"])

    def test_predict_type(self):
        parser = QueryParser(self.SQL_PREDICT_TEXT_CLASSIFICATION)
        self.assertEqual(parser.getType(), "PREDICT")

    def test_predict_params_classification(self):
        parser = QueryParser(self.SQL_PREDICT_TEXT_CLASSIFICATION)
        (
            input_query,
            model_name,
            input_schema,
            input_table,
            input_column,
            input_values,
            limit,
            order_by,
        ) = parser.getPredictParams()
        # print(input_query, model_name, input_schema, input_table, input_column, input_values, limit, order_by)
        self.assertEqual(model_name, "text_classification")
        self.assertEqual(input_schema, "mldb")
        self.assertEqual(input_table, "movie")
        self.assertEqual(input_column, "overview")
        self.assertEqual(input_values["labels"], "drama,comedy")
        self.assertEqual(limit, 1000)
        self.assertEqual(input_query, self.SQL_PREDICT_TEXT_CLASSIFICATION_INPUT_QUERY)

    def test_predict_create_output_table(self):
        (
            sql,
            table_schema,
            table_name,
        ) = SqlGenerator().scriptCreateTextClassificationPredictOutputTable(
            predict_id="002", labels=["comedy", "drama", "others"]
        )
        print(sql)

    def test_predict_insert_output_table(self):
        sql = SqlGenerator().scriptInsertTextPredictOutputTable(
            predict_id="002",
            text="Two imprisoned men's bond over a number of year",
            params=[
                ("drama", 0.8198206424713135),
                ("others", 0.1657235324382782),
                ("fantasy", 0.014455776661634445),
            ],
        )
        print(sql)

    def test_predict_join_output_table_text_classification(self):
        sql = SqlGenerator().scriptJoinSelectPredictOutputTable(
            select_table="movie",
            select_params=["*"],
            predict_table_name="_predict_123",
            predict_table_schema="model",
            input_schema="mldb",
            input_table="movie",
            input_column="overview",
            model_type="text_classification",
            where_condition=None,
            order_by=None,
            order_direction=None,
            limit=None,
        )
        sql_expected = "SELECT * FROM mldb.movie join model._predict_123 as predictions on predictions.inputs = mldb.movie.overview"
        self.assertEqual(sql, sql_expected)

    def test_predict_params_question_answering(self):
        parser = QueryParser(self.SQL_PREDICT_QUESTION_ANSWERING)
        (
            input_query,
            model_name,
            input_schema,
            input_table,
            input_column,
            input_values,
            limit,
            order_by,
        ) = parser.getPredictParams()
        self.assertEqual(input_query, "SELECT overview from mldb.movie ")
        self.assertEqual(
            input_values["question"], "Who is the main character of the movie"
        )
        self.assertEqual(order_by, None)

    def test_predict_join_output_table_question_answering(self):
        sql = SqlGenerator().scriptJoinSelectPredictOutputTable(
            select_table="movie",
            select_params=["*"],
            predict_table_name="_predict_123",
            predict_table_schema="model",
            input_schema="mldb",
            input_table="movie",
            input_column="overview",
            model_type="question_answering",
            where_condition=None,
            order_by=None,
            order_direction=None,
            limit=None,
        )
        sql_expected = "SELECT * FROM mldb.movie join model._predict_123 as predictions on predictions.inputs = mldb.movie.overview"
        self.assertEqual(sql, sql_expected)

    def test_predict_params_text_generation(self):
        parser = QueryParser(self.SQL_PREDICT_TEXT_GENERATION)
        (
            input_query,
            model_name,
            input_schema,
            input_table,
            input_column,
            input_values,
            limit,
            order_by,
        ) = parser.getPredictParams()
        self.assertEqual(
            input_query, "SELECT overview from mldb.movie WHERE mldb.movie._id = 12"
        )
        self.assertEqual(
            input_values["prompt"],
            " What type of audience will like movie? This movie is best for people who like",
        )
        self.assertEqual(order_by, None)


if __name__ == "__main__":
    unittest.main()
