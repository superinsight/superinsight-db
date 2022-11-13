import unittest
from database.sql.rewriter import SqlRewriter

class TestRewriterQuery(unittest.TestCase):


    SQL_REMOVE_MODEL_IN_WHERE = "SELECT overview from mldb.movie WHERE mldb.movie._id = 8 and predictions.score > 0.3 order by predictions.score"
    
    def test_predict_join_output_table_question_answering(self):
      sql = SqlRewriter(sql = self.SQL_REMOVE_MODEL_IN_WHERE).removeWhereCondition(full_table_name="predictions")
      print(sql)
      sql_expected = "SELECT overview from mldb.movie WHERE mldb.movie._id = 8 and 1 = 1 order by predictions.score"
      self.assertEqual(sql, sql_expected)

if __name__ == '__main__':
    unittest.main()