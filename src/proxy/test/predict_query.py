import unittest
from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator

class TestPredictQuery(unittest.TestCase):

    SQL_PREDICT_TEXT_CLASSIFICATION = "SELECT * FROM mldb.movie as movie JOIN model.text_classification as m on m.inputs = movie.overview JOIN model.text_classification as m on m.labels = ['drama,comedy'] WHERE mldb.movie._id = 2"
    SQL_PREDICT_TEXT_CLASSIFICATION_INPUT_QUERY = "SELECT overview from mldb.movie WHERE mldb.movie._id = 2"
    SQL_PREDICT_QUESTION_ANSWERING = "SELECT * FROM mldb.movie as movie JOIN model.question_answering m on m.inputs = movie.overview JOIN model.question_answering as m on m.question = ['Who is the main character of the movie'] WHERE movie._id = 8;"
    SQL_PREDICT_TEXT_GENERATION = "SELECT movie._id, movie.title, predictions.* FROM mldb.movie as movie JOIN model.text_generation m on m.inputs = movie.overview JOIN model.text_generation as m on m.stop_word = ['bull'] JOIN model.text_generation m on m.prompt = [' What type of audience will like movie? This movie is best for people who like'] WHERE mldb.movie._id = 12"


    '''
    def test_predict_type(self):
        parser = QueryParser(self.SQL_PREDICT_TEXT_CLASSIFICATION)
        self.assertEqual(parser.getType(), "PREDICT")
        
    def test_predict_params_classification(self):
        parser = QueryParser(self.SQL_PREDICT_TEXT_CLASSIFICATION)
        input_query, model_name, input_schema, input_table, input_column, input_values, limit, order_by = parser.getPredictParams()
        #print(input_query, model_name, input_schema, input_table, input_column, input_values, limit, order_by)
        self.assertEqual(model_name, "text_classification")
        self.assertEqual(input_schema, "mldb")
        self.assertEqual(input_table, "movie")
        self.assertEqual(input_column, "overview")
        self.assertEqual(input_values["labels"], "drama,comedy")
        self.assertEqual(limit, 1000)
        self.assertEqual(input_query, self.SQL_PREDICT_TEXT_CLASSIFICATION_INPUT_QUERY)
    
    def test_predict_join_output_table_text_classification(self):
      sql = SqlGenerator().scriptJoinSelectPredictOutputTable(
        select_table= "movie",
        select_params= ["*"],
        predict_table_name="_predict_123",
        predict_table_schema="model",
        input_schema="mldb",
        input_table="movie",
        input_column="overview",
        model_type= "text_classification",
        where_condition=None,
        order_by=None,
        order_direction=None,
        limit=None
      )
      sql_expected = "SELECT * FROM mldb.movie join model._predict_123 as predictions on predictions.inputs = mldb.movie.overview"
      self.assertEqual(sql, sql_expected)

    def test_predict_params_question_answering(self):
        parser = QueryParser(self.SQL_PREDICT_QUESTION_ANSWERING)
        input_query, model_name, input_schema, input_table, input_column, input_values, limit, order_by = parser.getPredictParams()
        self.assertEqual(input_query, "SELECT overview from mldb.movie ")
        self.assertEqual(input_values["question"], "Who is the main character of the movie")
        self.assertEqual(order_by, None)

    
    def test_predict_join_output_table_question_answering(self):
      sql = SqlGenerator().scriptJoinSelectPredictOutputTable(
        select_table= "movie",
        select_params= ["*"],
        predict_table_name="_predict_123",
        predict_table_schema="model",
        input_schema="mldb",
        input_table="movie",
        input_column="overview",
        model_type= "question_answering",
        where_condition=None,
        order_by=None,
        order_direction=None,
        limit=None
      )
      sql_expected = "SELECT * FROM mldb.movie join model._predict_123 as predictions on predictions.inputs = mldb.movie.overview"
      self.assertEqual(sql, sql_expected)

    def test_predict_params_text_generation(self):
        parser = QueryParser(self.SQL_PREDICT_TEXT_GENERATION)
        input_query, model_name, input_schema, input_table, input_column, input_values, limit, order_by = parser.getPredictParams()
        self.assertEqual(input_query, "SELECT overview from mldb.movie WHERE mldb.movie._id = 12")
        self.assertEqual(input_values["prompt"], " What type of audience will like movie? This movie is best for people who like")
        self.assertEqual(order_by, None)

        
    '''    
    def test_subquery_count(self):
        SQL_SUBQUERY= 'SELECT COUNT(1) AS "__record_count", "overview" from (SELECT * FROM mldb.movie JOIN model.summarization on model.summarization.inputs = mldb.movie.overview WHERE mldb.movie._id = 12) AS t GROUP BY "overview"'
        parser = QueryParser(SQL_SUBQUERY)
        input_query, model_name, input_schema, input_table, input_column, limit, order_by = parser.getPredictParams()
        print(input_query, model_name, input_schema, input_table, input_column, limit, order_by)
        self.assertEqual(input_query, "SELECT overview from mldb.movie WHERE mldb.movie._id = 12")
        self.assertEqual(model_name, "summarization")
        self.assertEqual(input_schema, "mldb")
        self.assertEqual(input_table, "movie")
        self.assertEqual(input_column, "overview")
        
if __name__ == '__main__':
    unittest.main()