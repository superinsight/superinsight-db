import unittest
from database.sql.query_parser import QueryParser

class TestCreateQuery(unittest.TestCase):

    SQL_CREATE = """CREATE TABLE mldb.table_name (_id serial PRIMARY KEY,
    	column1 TEXT,
    	column2 float8,
    	column3 varchar(100),
    	column4 int4);"""
    
    SQL_CREATE_SELECT = """CREATE table mldb.new_table AS
    	SELECT mldb.old_table._id, mldb.old_table.title, mldb.old_table.overview FROM mldb.old_table"""
    
    SQL_CREATE_PREDICT = """CREATE table mldb.new_table AS
    	SELECT mldb.old_table._id, mldb.old_table.title, mldb.old_table.overview FROM mldb.old_table
     	JOIN model.summarization
      	ON model.summarization.inputs = mldb.movie.overview"""

    SQL_ALTER_PRIMARY_KEY = """ALTER TABLE mldb.new_table ADD PRIMARY KEY (_id)"""

    def test_create_type(self):
        parser = QueryParser(self.SQL_CREATE)
        self.assertEqual(parser.getType(), "CREATE")
        parser = QueryParser(self.SQL_CREATE_SELECT)
        self.assertEqual(parser.getType(), "CREATE")
        parser = QueryParser(self.SQL_CREATE_PREDICT)
        self.assertEqual(parser.getType(), "CREATE")

    def test_create_with_select(self):
        create_statment, select_statement = QueryParser(self.SQL_CREATE_SELECT).getCreateWithSelectStatement()
        parser = QueryParser(select_statement)
        self.assertNotEqual(QueryParser(select_statement).getType(), "PREDICT")

    def test_create_with_select_predict(self):
        create_statment, select_statement = QueryParser(self.SQL_CREATE_PREDICT).getCreateWithSelectStatement()
        parser = QueryParser(select_statement)
        self.assertEqual(QueryParser(select_statement).getType(), "PREDICT")

    def test_alter_type(self):
        parser = QueryParser(self.SQL_ALTER_PRIMARY_KEY)
        print(parser.getType())
        print(parser.parsed.tables)
        self.assertEqual(parser.getType(), "ALTER")

if __name__ == '__main__':
    unittest.main()