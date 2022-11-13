from common.model_types import ModelTypes, ModelTypesValidation
from sql_metadata import Parser
import sys
import re
class QueryParser:

    sql = None
    parsed = None
    model_schema_name = "MODEL"

    def __init__(self, sql = None):
        self.sql = sql
        if self.sql is not None:
            self.parsed = Parser(sql)

    def formattedQuery(self):
        return self.parsed.without_comments.replace("`","\"")

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
            values = target[1:][:-1]
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
                if len(tables[0].split('.')) > 1:
                    schema = tables[0].split('.')[0]
                    table = tables[0].split('.')[1]
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
        return name.replace("[","").replace("]","")
        
    def getSafeColumns(self, columns):
        safeColumns = []
        for col in columns: 
            col = self.getSafeColumn(col)
            safeColumns.append(col)
        return safeColumns 

    def transformToken(self, condition, column, operator, value):
        if ("%" in value and operator == "="):
            value = value.replace("%","")
            operator = "similar"
        if (column == "_score"):
            column = "score"
        return (condition, column, operator, value)
       
    def removeWheres(self, wheres, schema_table_name_to_remove = None):
        valid_wheres = []
        if schema_table_name_to_remove is None:
            return wheres
        for where in wheres:
            schema, table, column, values = self.parseTableColumn(target=where)
            if not "{}.{}".format(schema,table).lower() == schema_table_name_to_remove.lower():
                valid_wheres.append(where)
        return valid_wheres
            
    def whereTokens(self, wheres):
        valid = False
        where_tokens = []
        for token in self.parsed.tokens:
            if valid and self.getSafeColumn(token.previous_token.value) in wheres and self.getSafeColumn(token.previous_token.previous_token).lower() in ["and","or","where"]:
                where_tokens.append(self.transformToken(self.getSafeColumn(token.previous_token.previous_token), self.getSafeColumn(token.previous_token), self.getSafeColumn(token), self.getSafeColumn(token.next_token)))
            if token.previous_token.value.lower() == "where" and self.getSafeColumn(token.value) == wheres[0]:
                valid = True
        return where_tokens

    def whereCondition(self, wheres):
        if wheres is None or len(wheres) == 0:
            return ""
        valid = False
        where_tokens = []
        for token in self.parsed.tokens:
            if valid and self.getSafeColumn(token.previous_token.value) in wheres and self.getSafeColumn(token.previous_token.previous_token).lower() in ["and","or","where"]:
                where_tokens.append(self.getSafeColumn(token.previous_token.previous_token))
                where_tokens.append(self.getSafeColumn(token.previous_token))
                where_tokens.append(self.getSafeColumn(token))
                where_tokens.append(self.getSafeColumn(token.next_token))
            if token.previous_token.value.lower() == "where" and self.getSafeColumn(token.value) == wheres[0]:
                valid = True
        return " ".join(where_tokens)
   
    def orderByDirection(self):
        schema, table, selects, join, wheres, where_tokens, offset, limit, order_by = self.getSelectParams()
        if order_by is None:
            return None
        tokens = [str(token) for token in self.parsed.tokens]
        valid = False
        for x in range(len(tokens)):
            token = tokens[x]
            if valid == True:
                if str(token) in order_by:
                    if token != tokens[-1]:
                        direction = tokens[x+1]
                        return direction
            if token.upper().replace(" ","") == "ORDERBY":
                valid = True
        return None

    def __appendNextToken(self, statement, token):
        if token is not None:
            statement = statement + token.value + " "
            return statement, token.next_token
        else:
            return None, None

    def getJoinStatements(self, only_include_tokens = [], exclude_tokens = []):
        join_statements = ""
        statement = ""
        for token in self.parsed.tokens:
            if token.value.lower() == "join":
                token_to_append = token
                while token_to_append is not None:
                    if len(statement) > 0 and token_to_append is not None and token_to_append.value.lower() in ["join", "where", "order", "limit"]:
                        exclude_statement = False
                        for exclude_token in exclude_tokens:
                            if exclude_token is not None and exclude_token in statement:
                                exclude_statement = True
                        if exclude_statement == False:
                            if only_include_tokens is not None and len(only_include_tokens) > 0:
                                for only_include_token in only_include_tokens:
                                    if only_include_token is not None and only_include_token.lower() in statement.lower():
                                        join_statements = join_statements + "\n" + statement
                                        break
                            else:
                                join_statements = join_statements + "\n" + statement
                        token_to_append = None
                        statement = ""
                    else:
                        statement, token_to_append = self.__appendNextToken(statement, token_to_append)
        if statement != "":
            join_statements = join_statements + "\n" + statement
        return join_statements

    def parseSelectParams(self):
        try:
            selects = []
            is_selection = False
            is_function_param = False
            select_param = None
            for token in self.parsed.tokens:
                if is_selection is True and token is not None and token.value.upper() != "FROM":
                    if str(token) == "(":
                        is_function_param = True
                    if str(token) == ")":
                        is_function_param = False
                    if str(token) == "," and is_function_param is False:
                        selects.append(select_param)
                        select_param = None
                    elif select_param is None:
                        select_param = str(token)
                    elif select_param is not None:
                        select_param = "{} {}".format(select_param, str(token))
                if token is not None and token.value.upper() == "SELECT":
                    is_selection = True
                if token is not None and token.value.upper() == "FROM":
                    is_selection = False
                    if select_param is not None:
                        selects.append(select_param)
                        select_param = None
            return selects
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return self.parsed.columns_dict["select"]


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
            tables = self.parsed.tables
            if tables is not None and len(tables) > 0:
                schema, table = self.parseTableName(tables[0])
            if self.parsed.columns_dict is not None: 
                if self.parsed.columns_dict.get("select") is not None:
                    selects = self.parseSelectParams()
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
            return schema, table, selects, join, wheres, where_tokens, offset, limit, order_by
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return None, None, None, None,None, None, None, None, None 

    def setDefaultLimit(self, limit):
        limit_and_offset = self.parsed.limit_and_offset
        if limit_and_offset is None:
            self.sql = "{} LIMIT {}".format(self.sql, limit)
            self.parsed = Parser(self.sql)


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
            self.setDefaultLimit(limit)
            if self.parsed.columns_dict is not None: 
                if self.parsed.columns_dict.get("join") is not None:
                    join_statement = self.getJoinStatements(only_include_tokens=ModelTypesValidation.getList("{}.".format(self.model_schema_name)))
                    for join_token in join_statement.split(" "):
                        schema, table, column, values = self.parseTableColumn(target=join_token)
                        if schema is not None and schema.upper() == self.model_schema_name:
                            model_name = table
                        elif schema is not None and table is not None and column is not None:
                            input_schema = schema
                            input_table = table 
                            input_column = column
                if self.parsed.columns_dict.get("order_by") is not None:
                    order_by = self.parsed.columns_dict["order_by"]
                if self.parsed.columns_dict.get("where") is not None:
                    wheres = self.getSafeColumns(self.parsed.columns_dict["where"])
                    if wheres is not None and len(wheres) > 0:
                        input_condition = self.whereCondition(wheres = wheres)
            if self.parsed.limit_and_offset is not None:
                limit = self.parsed.limit_and_offset[0]
            input_query = "SELECT {} from {}.{} {}".format(input_column, input_schema, input_table, input_condition)
            return input_query, model_name, input_schema, input_table, input_column, limit, order_by
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return None, None, None, None, None, None, None, None

    def getTrainParams(self):
        try:
            model_name = None
            model_type = None
            for token in self.parsed.tokens:
                if token.previous_token is not None and token.previous_token.previous_token is not None and token.previous_token.previous_token.value == "CREATE" and token.previous_token.value == "MODEL":
                    model_name = token.value
                    model_name = re.sub("^'", "", model_name)
                    model_name = re.sub("'$", "", model_name)
                if token.previous_token is not None and token.previous_token.previous_token is not None and token.previous_token.previous_token.value == "MODEL_NAME" and token.previous_token.value == "=":
                    model_type = token.value
                    model_type = re.sub("^'", "", model_type)
                    model_type = re.sub("'$", "", model_type)
            training_data = self.parsed.subqueries["training_data"]
            return model_name, model_type, training_data
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return None, None, None

    def isValid(self):
        try:
            return self.parsed is not None and self.parsed.query_type is not None
        except:
            return False

    def getType(self):
        _type = str(self.parsed.query_type).replace("QueryType.","")
        if (_type == "SELECT"):
            schema, table, selects, join, wheres, where_tokens, offset, limit, order_by = self.getSelectParams()
            if(join is not None):
                for join_table in join:
                    schema, table, column, values = self.parseTableColumn(target=join_table)
                    if schema is not None and schema.upper() == self.model_schema_name and ModelTypesValidation.exists(model_type = table):
                        return "PREDICT"
        return _type
        
                
            
