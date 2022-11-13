import logging
import psycopg2
class SqlHelper:

  logger = None

  def __init__(self, logger=None, handler = None):
    self.logger = logger or logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    if handler is not None:
      self.logger.addHandler(handler)
    self.logger.info("Init Database.SQL.SqlHelper...")

  def __del__(self):
    self.logger.info("Exit Database.SQL.SqlHelper...")

  def isAvailable(self, user, password, host, port, database):
      try:
          conn = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
          conn.close()
          return True
      except:
          return False

  def execute(self, user, password, host, port, database, sql):
    self.logger.info("Database.SQL.SqlHelper.execute...")
    if database is None:
      raise Exception("database is not defined")
    try:
      conn = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
      cursor = conn.cursor()
      print(sql)
      cursor.execute(sql)
      conn.commit()
    except (Exception, psycopg2.Error) as error:
      self.logger.error("Database.SQL.SqlHelper.execute:except - Error while fetching data from PostgreSQL", error)

    finally:
      # closing database connection.
      if conn:
        cursor.close()
        conn.close()
        self.logger.info("Database.SQL.SqlHelper.execute:finally - PostgreSQL conn is closed")
      return True