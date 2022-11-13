import unittest
from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator

class TestSelectQuery(unittest.TestCase):

    SQL_SELECT = "SELECT * FROM mldb.movie WHERE movie._id = 2"
    SQL_SELECT_ML = "SELECT * FROM mldb.movie WHERE movie.overview SIMILAR ('action')"

    def test_select_type(self):
        parser = QueryParser(self.SQL_SELECT)
        self.assertEqual(parser.getType(), "SELECT")
        
    def test_select_type_ml(self):
        parser = QueryParser(self.SQL_SELECT_ML)
        self.assertEqual(parser.getType(), "SELECT")

if __name__ == '__main__':
    unittest.main()