import unittest
from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator

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
    
    def test_create_table_log_script_create(self):
        sqldb = SqlGenerator()
        sql = sqldb.scriptCreateSystemLogTable()
        self.assertNotEqual(sql, None)

    def test_create_table_trigger_func_script_create(self):
        sqldb = SqlGenerator()
        sql = sqldb.scriptCreateLogTableTriggerFunction()
        self.assertNotEqual(sql, None)

    def test_create_table_trigger(self):
        sqldb = SqlGenerator()
        sql = sqldb.scriptWriteLogTrigger()
        self.assertNotEqual(sql, None)
        
    def test_create_table_trigger_script_create(self):
        sqldb = SqlGenerator(schema_name='bigstudio', table_name='movies')
        sql = sqldb.runScriptCreateTableAndTrigger(SQL_CREATE_TABLE)
        self.assertNotEqual(sql, None)
        
    def test_order_by_desc(self):
        sql = "SELECT * FROM predictions where predictions.score > 0.5 order by predictions.score desc"
        parser = QueryParser(sql)
        direction = parser.orderByDirection()
        self.assertEqual(direction, "desc")
        
if __name__ == '__main__':
    unittest.main()