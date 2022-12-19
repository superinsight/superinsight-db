import psycopg2
from psycopg2.extras import RealDictCursor
from environment import Environment
from common.logger import CommonLogger


class SqlHelper:

    logger = None
    postgres_user = None
    postgres_password = None
    postgres_host = None
    postgres_port = None
    postgres_database = None

    def __init__(self, logger=None, handler=None, database=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init Database.SQL.SqlHelper...")
        self.postgres_database = database
        self.postgres_user = Environment.postgres_user
        self.postgres_password = Environment.postgres_password
        host, port = self.getDatabaseConfig()
        self.postgres_host = host
        self.postgres_port = port

    def __del__(self):
        self.logger.info("Exit Database.SQL.SqlHelper...")

    def isAvailable(self):
        try:
            print(
                self.postgres_database,
                self.postgres_password,
                self.postgres_host,
                self.postgres_database,
                self.postgres_port,
            )
            conn = psycopg2.connect(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
            )
            conn.close()
            return True
        except:
            return False

    def getDatabaseConfig(self):
        host = Environment.postgres_host
        port = Environment.postgres_port
        self.logger.info(
            "Database.SQL.SqlHelper.getDatabaseConfig return:{}/{}/{}".format(
                self.postgres_database, host, port
            )
        )
        return host, port

    def execute(self, sql):
        self.logger.info("Database.SQL.SqlHelper.execute...")
        if self.postgres_database is None:
            raise Exception("database is not defined")

        rows = []
        try:
            conn = psycopg2.connect(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            self.logger.error(error)

        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                self.logger.info(
                    "Database.SQL.SqlHelper.execute:finally - PostgreSQL conn is closed"
                )
            return rows

    def read(self, sql=None, return_dict=False):
        self.logger.info("Database.SQL.SqlHelper.read...")
        if self.postgres_database is None:
            raise Exception("database is not defined")

        rows = []
        try:
            if return_dict:
                cursor_factory = RealDictCursor
            else:
                cursor_factory = None
            conn = psycopg2.connect(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
                cursor_factory=cursor_factory,
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            records = cursor.fetchall()
            for row in records:
                rows.append(row)
        except (Exception, psycopg2.Error) as error:
            self.logger.error(error)

        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                self.logger.info(
                    "Database.SQL.SqlHelper.read:finally - PostgreSQL conn is closed"
                )
            return rows

    def getPrimaryKey(self, table_schema, table_name):
        self.logger.info("Database.SQL.SqlHelper.getPrimaryKey...")
        primary_key = None
        if self.postgres_database is None:
            raise Exception("database is not defined")

        sql = """SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
      FROM   pg_index i
      JOIN   pg_attribute a ON a.attrelid = i.indrelid
                          AND a.attnum = ANY(i.indkey)
      WHERE  i.indrelid = '{}.{}'::regclass
      AND    i.indisprimary;    
    """.format(
            table_schema, table_name
        )
        try:
            conn = psycopg2.connect(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is not None and row[0] is not None:
                primary_key = row[0]
        except (Exception, psycopg2.Error) as error:
            self.logger.error(error)

        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                self.logger.info(
                    "Database.SQL.SqlHelper.getPrimaryKey:finally - PostgreSQL conn is closed"
                )
            return primary_key
