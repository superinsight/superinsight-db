import unittest
from database.sql.rewriter import SqlRewriter
from sql_metadata import Parser

class TestRewriterQuery(unittest.TestCase):

    def test_predict_join_output_table_question_answering(self):
      SQL_REMOVE_MODEL_IN_WHERE = "SELECT overview from mldb.movie WHERE mldb.movie._id = 8 and predictions.score > 0.3 order by predictions.score"
      sql = SqlRewriter(sql = SQL_REMOVE_MODEL_IN_WHERE).removeWhereCondition(full_table_name="predictions")
      print(sql)
      sql_expected = "SELECT overview from mldb.movie WHERE mldb.movie._id = 8     order by predictions.score"
      self.assertEqual(sql, sql_expected)

    def test_semantic_search(self):
      SQL_SEMANTIC_SEARCH = """select mldb.product_7.image as image, predictions.score as score from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.image where model.semantic_search.similar = 'https://cdn-v4.petpetgo.com/600/public/333311c4-c5eb-48a7-a742-6750d9eb00a3.jpg'"""
      sql = SqlRewriter(sql = SQL_SEMANTIC_SEARCH, db_database="demo", db_user= "proxy_admin").rewrite()
      sql_starts_with_expected = """SELECT mldb.product_7.image as image , predictions.score as score FROM mldb.product_7 join model._predict_"""
      self.assertTrue(sql.startswith(sql_starts_with_expected))

    def test_semantic_search_with_concat_text(self):
      SQL_SEMANTIC_SEARCH = """select mldb.product_7.title, CONCAT('xx',mldb.product_7.description) as concat_desc from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.description where model.semantic_search.similar = 'healthy food'"""
      sql = SqlRewriter(sql = SQL_SEMANTIC_SEARCH, db_database="demo", db_user= "proxy_admin").rewrite()
      sql_starts_with_expected = """SELECT mldb.product_7.title , CONCAT ( 'xx' , mldb.product_7.description ) as concat_desc FROM mldb.product_7"""
      self.assertTrue(sql.startswith(sql_starts_with_expected))

    def test_semantic_search_with_concat_img(self):
      SQL_SEMANTIC_SEARCH = """select mldb.product_7.title, CONCAT('<img src="', mldb.product_7.image, '" alt="my_image" />') as concat_img from mldb.product_7 join model.semantic_search on model.semantic_search.inputs = mldb.product_7.description where model.semantic_search.similar = 'healthy food'"""
      sql = SqlRewriter(sql = SQL_SEMANTIC_SEARCH, db_database="demo", db_user= "proxy_admin").rewrite()
      sql_starts_with_expected = """SELECT mldb.product_7.title , CONCAT ( '<img src="' , mldb.product_7.image , '" alt="my_image" />' ) as concat_img FROM mldb.product_7"""
      self.assertTrue(sql.startswith(sql_starts_with_expected))

    def test_subquery_count(self):
      SQL_SUBQUERY= 'SELECT COUNT(1) AS "__record_count", "overview" from (SELECT * FROM mldb.movie JOIN model.summarization on model.summarization.inputs = mldb.movie.overview WHERE mldb.movie._id < 4) AS t GROUP BY "overview"'
      sql = SqlRewriter(sql = SQL_SUBQUERY, db_database="demo", db_user= "demo_admin").rewrite()
      print(sql)
      
    def test_subquery_count_google_data_studio(self):
      SQL_SUBQUERY= 'SELECT COUNT(1) AS "qt_sfleohs9xc", "title" FROM (SELECT mldb.movie._id, mldb.movie.title, mldb.movie.overview FROM mldb.movie JOIN model.semantic_search ON model.semantic_search.inputs = mldb.movie.overview WHERE mldb.movie._id < 19 AND model.semantic_search.similar = ''gangster'') AS t GROUP BY "title"'
      sql = SqlRewriter(sql = SQL_SUBQUERY, db_database="demo", db_user= "demo_admin").rewrite()
      print(sql)

    def test_recommender_train(self):
      SQL_TRAIN = """CREATE MODEL model.product_recommender_model FROM (SELECT userid as user_id, productid as item_id, rating as rating, "timestamp" as "timestamp" FROM mldb.products) as training_data WHERE MODEL_NAME = 'recommender'"""
      sql = SqlRewriter(sql = SQL_TRAIN, db_database="demo", db_user= "demo_admin").rewrite()
      print(sql)

    def test_recommender_predict(self):
      SQL_PREDICT = """SELECT predictions.*, mldb.movie_rating.movieid
      FROM mldb.movie_rating
      JOIN model.recommender ON model.recommender.user_id = mldb.movie_rating.userid
      WHERE model.recommender.model_id = 'f48df19f48c3fe9d7c0f5ad215e45891' and mldb.movie_rating.userid < 4 and model.recommender.item_id = mldb.movie_rating.movieid
      order by predictions.score desc
      """
      sql = SqlRewriter(sql = SQL_PREDICT, db_database="demo", db_user= "proxy_admin").rewrite()
      print("*****")
      print(sql)

    def test_recommender_predict_join_multiple_Tables(self):
      SQL_PREDICT = """SELECT predictions.*, mldb.movie_rating.movieid
      FROM mldb.movie_rating
      JOIN mldb.movie ON mldb.movie._id = predictions.item_id::int 
      JOIN model.recommender ON model.recommender.user_id = mldb.movie_rating.userid
      WHERE model.recommender.model_id = 'a06a691ce8bb5067bfe9b60b0bc361e3' and mldb.movie_rating.userid = 2 and model.recommender.item_id = mldb.movie_rating.movieid
      order by predictions.score desc
      """
      sql = SqlRewriter(sql = SQL_PREDICT, db_database="demo", db_user= "proxy_admin").rewrite()
      print("*****")
      print(sql)

if __name__ == '__main__':
    unittest.main()