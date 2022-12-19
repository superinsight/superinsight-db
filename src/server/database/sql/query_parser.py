from sql_metadata import Parser
import sys


class QueryParser:

    sql = None
    parsed = None
    model_schema_name = "MODEL"

    def __init__(self, sql=None):
        self.sql = sql
        if self.sql is not None:
            self.parsed = Parser(sql)

    def parseTableName(self, target):
        schema = None
        table = None
        if len(target.split(".")) > 1:
            schema = target.split(".")[0]
            table = target.split(".")[1]
        elif len(target.split(".")) > 0:
            table = target.split(".")[0]
        return schema, table

    def parseTableColumn(self, target):
        schema = None
        table = None
        column = None
        values = None
        if target.startswith("[") and target.endswith("]"):
            values = target.replace("['", "").replace("']", "")
        elif len(target.split(".")) > 2:
            schema = target.split(".")[0]
            table = target.split(".")[1]
            column = target.split(".")[2]
        elif len(target.split(".")) > 1:
            table = target.split(".")[0]
            column = target.split(".")[1]
        elif len(target.split(".")) > 0:
            column = target.split(".")[0]
        return schema, table, column, values

    def getInsertParams(self):
        try:
            tables = self.parsed.tables
            columns = self.parsed.columns
            values = self.parsed.values
            tokens = self.parsed.tokens
            return tables, columns, values, tokens
        except:
            return None, None, None, None

    def getCreateParams(self):
        try:
            tables = self.parsed.tables
            columns = self.parsed.columns
            values = self.parsed.values
            tokens = self.parsed.tokens
            if tables is not None and len(tables) > 0:
                if len(tables[0].split(".")) > 1:
                    schema = tables[0].split(".")[0]
                    table = tables[0].split(".")[1]
                else:
                    table = tables[0]
            return schema, table, columns, values, tokens
        except:
            return None, None, None, None, None

    def getSafeColumn(self, name):
        name = str(name)
        if name == "text":
            name = "_text_"
        if name == "[text]":
            name = "_text_"
        if name == "comment":
            name = "_comment_"
        if name == "[comment]":
            name = "_comment_"
        return name.replace("[", "").replace("]", "")

    def getSafeColumns(self, columns):
        safeColumns = []
        for col in columns:
            col = self.getSafeColumn(col)
            safeColumns.append(col)
        return safeColumns

    def transformToken(self, condition, column, operator, value):
        if "%" in value and operator == "=":
            value = value.replace("%", "")
            operator = "similar"
        if column == "_score":
            column = "score"
        return (condition, column, operator, value)

    def whereTokens(self, wheres):
        valid = False
        where_tokens = []
        for token in self.parsed.tokens:
            if (
                valid
                and self.getSafeColumn(token.previous_token.value) in wheres
                and self.getSafeColumn(token.previous_token.previous_token).lower()
                in ["and", "or", "where"]
            ):
                where_tokens.append(
                    self.transformToken(
                        self.getSafeColumn(token.previous_token.previous_token),
                        self.getSafeColumn(token.previous_token),
                        self.getSafeColumn(token),
                        self.getSafeColumn(token.next_token),
                    )
                )
            if (
                token.previous_token.value.lower() == "where"
                and self.getSafeColumn(token.value) == wheres[0]
            ):
                valid = True
        return where_tokens

    def whereCondition(self, wheres):
        valid = False
        where_tokens = []
        for token in self.parsed.tokens:
            if (
                valid
                and self.getSafeColumn(token.previous_token.value) in wheres
                and self.getSafeColumn(token.previous_token.previous_token).lower()
                in ["and", "or", "where"]
            ):
                where_tokens.append(
                    self.getSafeColumn(token.previous_token.previous_token)
                )
                where_tokens.append(self.getSafeColumn(token.previous_token))
                where_tokens.append(self.getSafeColumn(token))
                where_tokens.append(self.getSafeColumn(token.next_token))
            if (
                token.previous_token.value.lower() == "where"
                and self.getSafeColumn(token.value) == wheres[0]
            ):
                valid = True
        return " ".join(where_tokens)

    def orderByDirection(self):
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
        ) = self.getSelectParams()
        if order_by is None:
            return None
        tokens = [str(token) for token in self.parsed.tokens]
        valid = False
        for x in range(len(tokens)):
            token = tokens[x]
            if valid == True:
                if str(token) in order_by:
                    if token != tokens[-1]:
                        direction = tokens[x + 1]
                        return direction
            if token.upper().replace(" ", "") == "ORDERBY":
                valid = True
        return None

    def getWhereValues(self, table_schema, table_name, table_column):
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
        ) = self.getSelectParams()
        if where_tokens is None:
            return None
        for where_token in where_tokens:
            schema, table, column, values = self.parseTableColumn(target=where_token[1])
            if (
                schema is not None
                and table_schema.lower() == schema.lower()
                and table_name.lower() == table.lower()
                and table_column.lower() == column.lower()
            ):
                values = where_token[3]
                if values.startswith("'") and values.endswith("'"):
                    values = values[1:][:-1]
                return values
        return None

    def getSelectParams(self):
        try:
            schema = None
            table = None
            limit = 1000
            selects = None
            join = None
            offset = None
            wheres = None
            where_tokens = None
            order_by = None
            scoring = False
            tables = self.parsed.tables
            if tables is not None and len(tables) > 0:
                schema, table = self.parseTableName(tables[0])
            if self.parsed.columns_dict is not None:
                if self.parsed.columns_dict.get("selects") is not None:
                    selects = self.parsed.columns_dict["select"]
                if self.parsed.columns_dict.get("join") is not None:
                    join = self.parsed.columns_dict["join"]
                if self.parsed.columns_dict.get("order_by") is not None:
                    order_by = self.parsed.columns_dict["order_by"]
                if self.parsed.columns_dict.get("where") is not None:
                    wheres = self.getSafeColumns(self.parsed.columns_dict["where"])
                    if wheres is not None and len(wheres) > 0:
                        where_tokens = self.whereTokens(wheres)
            if self.parsed.limit_and_offset is not None:
                limit = self.parsed.limit_and_offset[0]
                offset = self.parsed.limit_and_offset[1]
            if (
                where_tokens is not None
                and len([item for item in where_tokens if item[2].lower() == "similar"])
                > 0
            ):
                scoring = True

            return (
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
            )
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return None, None, None, None, None, None, None, None, None, None

    def getPredictParams(self):
        try:
            limit = 1000
            join = None
            wheres = None
            order_by = None
            model_name = None
            input_schema = None
            input_table = None
            input_column = None
            input_condition = ""
            input_values = {}
            if self.parsed.columns_dict is not None:
                if self.parsed.columns_dict.get("join") is not None:
                    join = self.parsed.columns_dict["join"]
                    for x in range(len(join)):
                        join_table = join[x]
                        schema, table, column, values = self.parseTableColumn(
                            target=join_table
                        )
                        if (
                            schema is not None
                            and schema.upper() == self.model_schema_name
                        ):
                            model_name = table
                        elif values is not None:
                            (
                                last_schema,
                                last_table,
                                last_column,
                                last_values,
                            ) = self.parseTableColumn(target=join[x - 1])
                            input_values[last_column] = values
                        elif (
                            schema is not None
                            and table is not None
                            and column is not None
                        ):
                            input_schema = schema
                            input_table = table
                            input_column = column
                if self.parsed.columns_dict.get("order_by") is not None:
                    order_by = self.parsed.columns_dict["order_by"]
                if self.parsed.columns_dict.get("where") is not None:
                    wheres = self.getSafeColumns(self.parsed.columns_dict["where"])
                    if wheres is not None and len(wheres) > 0:
                        input_condition = self.whereCondition(wheres)
            if self.parsed.limit_and_offset is not None:
                limit = self.parsed.limit_and_offset[0]
            input_query = "SELECT {} from {}.{} {}".format(
                input_column, input_schema, input_table, input_condition
            )
            return (
                input_query,
                model_name,
                input_schema,
                input_table,
                input_column,
                input_values,
                limit,
                order_by,
            )
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return None, None, None, None, None, None, None, None

    def isValid(self):
        try:
            return self.parsed is not None and self.parsed.query_type is not None
        except:
            return False

    def getType(self):
        _type = str(self.parsed.query_type).replace("QueryType.", "")
        if _type == "SELECT":
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
            ) = self.getSelectParams()
            if join is not None:
                for join_table in join:
                    schema, table, column, values = self.parseTableColumn(
                        target=join_table
                    )
                    if schema is not None and schema.upper() == self.model_schema_name:
                        return "PREDICT"
        return _type
