from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator
from database.sql.helper import SqlHelper
from common.logger import CommonLogger

"""
ToDo: Introduce Dependency Injection for predictor and generator for Unit Test Without DB and API Access
"""


class SqlRewriter:

    logger = None
    sql = None
    generator = None

    def __init__(self, logger=None, handler=None, sql=None, generator=SqlGenerator()):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init Database.SQL.SqlRewriter...")
        self.sql = sql
        self.generator = generator

    def __del__(self):
        self.logger.info("Exit Database.SQL.SqlRewriter...")

    def alterToSemanticSearchQuery(self, database, sql, similar):
        parser = QueryParser(sql=sql)
        sql_helper = SqlHelper(database=database)
        (
            schema,
            table,
            selects,
            join,
            wheres,
            where_tokens,
            offset,
            limit,
            order_by,
            scoring,
        ) = parser.getSelectParams()
        primary_key_values = None
        if (
            wheres is not None
            and selects is not None
            and wheres is not None
            and len(wheres) > 0
        ):
            where_conditions = parser.whereCondition(wheres)
            primary_key = sql_helper.getPrimaryKey(
                table_schema=schema, table_name=table
            )
            if primary_key is not None:
                sql = "SELECT {} FROM {}.{} {}".format(
                    primary_key, schema, table, where_conditions
                )
                rows = sql_helper.read(sql)
                primary_key_values = [str(row[0]) for row in rows]
        return similar, primary_key_values

    def removeWhereCondition(self, sql=None, full_table_name=None):
        if sql is None:
            sql = self.sql
        if full_table_name == None:
            return sql
        parser = QueryParser(sql)
        (
            schema,
            table,
            selects,
            join,
            wheres,
            where_tokens,
            offset,
            limit,
            order_by,
            scoring,
        ) = parser.getSelectParams()
        tokens = [str(token) for token in parser.parsed.tokens]
        where_was_removed = False
        if wheres is not None and len(wheres) > 0:
            for x in range(len(tokens)):
                token = tokens[x]
                if token is not None and token.upper().replace(" ", "") == "ORDERBY":
                    break
                if token is not None and str(token) in wheres:
                    schema, table, column, values = parser.parseTableColumn(
                        target=token
                    )
                    if table == full_table_name:
                        if tokens[x - 1].lower() == "where":
                            where_was_removed = True
                        tokens[x - 1] = ""
                        tokens[x] = ""
                        tokens[x + 1] = ""
                        tokens[x + 2] = ""
        if tokens is not None and len(tokens) > 0:
            for x in range(len(tokens)):
                if where_was_removed and (
                    tokens[x].upper() == "AND" or tokens[x].upper() == "OR"
                ):
                    tokens[x] = "WHERE"
                    break
            sql = " ".join(tokens)
        return sql
