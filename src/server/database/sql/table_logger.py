import psycopg2
from database.sql.helper import SqlHelper
from environment import Environment
from common.logger import CommonLogger


class TableLogger:

    logger = None
    database = None
    postgres_user = None
    postgres_password = None
    postgres_host = None
    postgres_port = None
    postgres_database = None
    postgres_system_schema = "system"
    table_logs_read_size = None

    def __init__(self, logger=None, handler=None, database=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        if database is None:
            self.logger.warning("database has not been assigned for SQL.TableLogger")
        else:
            self.database = database
            self.logger.info(
                "Init SQL.TableLogger for database: {}...".format(database)
            )
        self.database = database
        self.postgres_user = Environment.postgres_user
        self.postgres_password = Environment.postgres_password
        host, port = SqlHelper(database=self.database).getDatabaseConfig()
        self.postgres_host = host
        self.postgres_port = port
        self.postgres_database = self.database
        self.table_logs_read_size = Environment.table_logs_read_size

    def __del__(self):
        self.logger.info("Exit TableLogger...")

    def readRecentUpdates(self, primary_key_name, primary_key_value, version_after_id):
        if version_after_id is None:
            version_after_id = 0
        recent_updates = self._readRecentUpdates(
            primary_key_name=primary_key_name,
            primary_key_value=primary_key_value,
            version_after_id=version_after_id,
        )
        version = 0
        tables = []
        if recent_updates is not None and len(recent_updates) > 0:
            version = recent_updates[-1]["_id"]
            tables_row_changed = {}
            for changed in recent_updates:
                id = "{}_{}_{}".format(
                    changed["table_schema"],
                    changed["table_name"],
                    changed["column_name"],
                )
                if tables_row_changed.get(id) is None:
                    tables_row_changed[id] = []
                tables_row_changed[id].append(changed)
            for id in tables_row_changed:
                table = {}
                table["version"] = version
                table["rows"] = tables_row_changed[id]
                table["table_schema"] = table["rows"][0]["table_schema"]
                table["table_name"] = table["rows"][0]["table_name"]
                table["column_name"] = table["rows"][0]["column_name"]
                tables.append(table)
        return tables

    def _readRecentUpdates(self, primary_key_name, primary_key_value, version_after_id):
        if version_after_id is None:
            version_after_id = 0
        self.logger.info(
            "TableLogger.readRecentUpdates Primary Key: {}={} and version_after_id {}".format(
                primary_key_name, primary_key_value, version_after_id
            )
        )
        changes = []
        conn = psycopg2.connect(
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_database,
        )
        try:
            cursor = conn.cursor()
            postgreSQL_select_Query = """
      SELECT _id, table_schema, table_name, primary_key_name, primary_key_value, column_name, column_value, operation, created_on
      FROM {}.table_logs where (operation = 'INSERT' or operation = 'UPDATE' or operation = 'DELETE' or operation = 'TRUNCATE')
      and _id > {}
      and _id > (select coalesce((SELECT column_value FROM {}.table_logs where operation = 'INDEXING' and ((primary_key_name= '{}' and primary_key_value= '{}')) and column_name ='_id' order by _id DESC limit 1)::numeric , 0))
      ORDER BY "_id" ASC 
      LIMIT {}
      """.format(
                self.postgres_system_schema,
                version_after_id,
                self.postgres_system_schema,
                primary_key_name,
                primary_key_value,
                self.table_logs_read_size,
            )
            self.logger.info(postgreSQL_select_Query)
            cursor.execute(postgreSQL_select_Query)
            records = cursor.fetchall()
            for row in records:
                changed = {}
                changed["_id"] = row[0]
                changed["table_schema"] = row[1]
                changed["table_name"] = row[2]
                changed["primary_key_name"] = row[3]
                changed["primary_key_value"] = row[4]
                changed["column_name"] = row[5]
                changed["column_value"] = row[6]
                changed["operation"] = row[7]
                changed["created_on"] = row[7]
                changes.append(changed)
        except (Exception, psycopg2.Error) as error:
            self.logger.error(error)

        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                self.logger.info("PostgreSQL conn is closed")
            return changes

    def readTables(self):
        self.logger.info("TableLogger.readTables...")
        tables = []
        try:
            conn = psycopg2.connect(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
            )
            cursor = conn.cursor()
            postgreSQL_select_Query = """
      SELECT distinct table_schema, table_name, column_name
      FROM {}.table_logs
      where table_schema != '{}' and (operation = 'INSERT' or operation = 'UPDATE' or operation = 'DELETE' or operation = 'TRUNCATE')
      """.format(
                self.postgres_system_schema, self.postgres_system_schema
            )
            cursor.execute(postgreSQL_select_Query)
            records = cursor.fetchall()
            for row in records:
                table = {}
                table["table_schema"] = row[0]
                table["table_name"] = row[1]
                table["column_name"] = row[2]
                tables.append(table)
        except (Exception, psycopg2.Error) as error:
            self.logger.error(error)

        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                self.logger.info(
                    "TableLogger.readTables:finally - PostgreSQL conn is closed"
                )
            return tables

    def insertTableLog(
        self, last_row_id, operation, primary_key_name, primary_key_value
    ):
        sql = "INSERT INTO {}.table_logs(table_schema, table_name , primary_key_name, primary_key_value, column_name, column_value, operation, created_on) VALUES('{}', 'table_logs', '{}', '{}', '_id', {}, '{}', current_timestamp) RETURNING *;"
        self.logger.info("TableLogger.insertTableLog for SQL: {}".format(sql))
        conn = None
        row_id = None
        try:
            conn = psycopg2.connect(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
            )
            # create a new cursor
            cur = conn.cursor()
            # execute the INSERT statement
            cur.execute(
                sql.format(
                    self.postgres_system_schema,
                    self.postgres_system_schema,
                    primary_key_name,
                    primary_key_value,
                    last_row_id,
                    operation,
                )
            )
            # get the generated id back
            row_id = cur.fetchone()[0]
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()
        self.logger.info(
            "TableLogger.insertTableLog inserted row id: {}".format(row_id)
        )
        return row_id
