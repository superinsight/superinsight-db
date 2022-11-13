import unittest
from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator
from sql_metadata import Parser

SQL_CREATE_TABLE = "CREATE TABLE bigstudio.movies (movie_id serial PRIMARY KEY, movie_name VARCHAR ( 50 ) NOT NULL, movie_description TEXT, created_on TIMESTAMP NOT NULL);"
sql = "INSERT INTO table_name (column1, column2, column3) VALUES ('value1', 'value2', 'value3');returning *"
sqlbatch = "INSERT INTO table_name (column1, column2, column3)\nSELECT value1, value2, value3 FROM manyvalues;returning *"

class TestSqlParser(unittest.TestCase):

    def test_create_table_is_valid(self):
        parser = QueryParser(SQL_CREATE_TABLE)
        self.assertEqual(parser.isValid(), True)

    def test_create_table_type(self):
        parser = QueryParser(SQL_CREATE_TABLE)
        self.assertEqual(str(parser.getType()), 'CREATE')

    def test_create_table_schema(self):
        parser = QueryParser(SQL_CREATE_TABLE)
        schema, table, columns, values, tokens = parser.getCreateParams()
        self.assertEqual(schema, 'bigstudio')
        self.assertEqual(table, 'movies')
        self.assertEqual(columns, ['movie_id', 'movie_name', 'movie_description', 'created_on'])
    
    def test_create_table_trigger_script_create(self):
        sqldb = SqlGenerator(schema_name='bigstudio', table_name='movies')
        sql = sqldb.runScriptCreateTableAndTrigger(SQL_CREATE_TABLE)
        self.assertNotEqual(sql, None)
        
    def test_order_by_desc(self):
        sql = "SELECT * FROM predictions where predictions.score > 0.5 order by predictions.score desc"
        parser = QueryParser(sql)
        direction = parser.orderByDirection()
        self.assertEqual(direction, "desc")

    def test_auto_append_limit(self):
        limit = 100
        sql = """select mldb.product_7.image, predictions.score, predictions.* from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.image"""
        parser = QueryParser(sql)
        parser.setDefaultLimit(limit)
        limit_and_offset = parser.parsed.limit_and_offset
        self.assertEqual(limit, limit_and_offset[0])

    def test_auto_append_limit_expect_no_change(self):
        limit = 100
        sql = """select mldb.product_7.image, predictions.score, predictions.* from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.image limit 1000"""
        parser = QueryParser(sql)
        parser.setDefaultLimit(limit)
        limit_and_offset = parser.parsed.limit_and_offset
        self.assertEqual(1000, limit_and_offset[0])

    def test_auto_append_limit_with_offset(self):
        limit = 100
        sql = """select mldb.product_7.image, predictions.score, predictions.* from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.image offset 10"""
        parser = QueryParser(sql)
        parser.setDefaultLimit(limit)
        limit_and_offset = parser.parsed.limit_and_offset
        self.assertEqual(limit, limit_and_offset[0])

    def test_auto_append_limit_offset_expect_no_change(self):
        limit = 100
        sql = """select mldb.product_7.image, predictions.score, predictions.* from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.image offset 10 limit 1000"""
        parser = QueryParser(sql)
        parser.setDefaultLimit(limit)
        limit_and_offset = parser.parsed.limit_and_offset
        self.assertEqual(1000, limit_and_offset[0])

    def test_recommender_predict_join_multiple_Tables(self):
        sql = """SELECT predictions.*, mldb.movie_rating.movieid
        FROM mldb.movie_rating
        JOIN model.recommender ON model.recommender.user_id = mldb.movie_rating.userid
        JOIN mldb.movie ON mldb.movie._id = predictions.item_id::int 
        WHERE model.recommender.model_id = 'a06a691ce8bb5067bfe9b60b0bc361e3' and mldb.movie_rating.userid = 2 and model.recommender.item_id = mldb.movie_rating.movieid
        order by predictions.score desc
        """
        parser = QueryParser(sql)
        join_statements = parser.getJoinStatements(exclude_tokens=["model.recommender"])
        self.assertEqual(join_statements, "\nJOIN mldb.movie ON mldb.movie._id = predictions.item_id :: int ")

if __name__ == '__main__':
    unittest.main()