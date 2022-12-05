import logging
from common.model_types import ModelTypes
from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator
from api.ml.predictor import Predictor
from api.ml.trainer import Trainer

class SqlRewriter:

  logger = None
  sql = None
  predictor = None
  generator = None

  def __init__(self, logger=None, handler = None, sql = None, db_database = None, db_user = None):
    self.logger = logger or logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    if handler is not None:
      self.logger.addHandler(handler)
    self.logger.info("Init Database.SQL.SqlRewriter...")
    self.sql = sql
    self.predictor = Predictor(db_database = db_database, db_user = db_user)
    self.trainer = Trainer(db_database = db_database, db_user = db_user)
    self.generator = SqlGenerator()

  def __del__(self):
    self.logger.info("Exit Database.SQL.SqlRewriter...")

  def rewrite(self):
    parser = QueryParser(self.sql)
    return_sql = parser.formattedQuery()
    if str(parser.getType()) == 'CREATE':
      return self.__rewriteQueryCreate(sql=return_sql)
    if str(parser.getType()) == 'TRAIN':
      return self.__rewriteQueryTrain(sql=return_sql)
    else:
      for subquery_name in parser.parsed.subqueries_names:
        sub_query = QueryParser(parser.parsed.subqueries[subquery_name]).formattedQuery()
        transformed_sub_query = self.__rewriteQueryPredict(sql = sub_query)
        return_sql = return_sql.replace(sub_query, transformed_sub_query)
      return self.__rewriteQueryPredict(sql=return_sql)

  def __rewriteQueryCreate(self, sql = None):
    if sql is None:
      sql = self.sql
    parser = QueryParser(sql)
    if str(parser.getType()) != 'CREATE':
      return sql
    if parser.parsed.columns_dict is None:
      schema, table, _, _, _ = parser.getCreateParams()
      query = SqlGenerator(schema_name=schema, table_name=table).runScriptCreateTableAndTrigger(sql)
      return query
    create_statement, select_statement = parser.getCreateWithSelectStatement()
    if QueryParser(select_statement).getType() == "PREDICT":
      transformed_select_statement = self.__rewriteQueryPredict(sql = select_statement)
      transformed_sql = "{}\n{}".format(create_statement, transformed_select_statement)
      schema, table, _, _, _ = parser.getCreateParams()
      sql = SqlGenerator(schema_name=schema, table_name=table).runScriptCreateTableAndTrigger(transformed_sql)
    return sql

  def __rewriteQueryPredict(self, sql = None, output_schema = None, output_table = None):
    if sql is None:
      sql = self.sql
    parser = QueryParser(sql)
    if str(parser.getType()) != 'PREDICT':
      return sql
    input_query, model_name, input_schema, input_table, input_column, limit, order_by = parser.getPredictParams()
    schema, table, selects, join, wheres, where_tokens, offset, limit, order_by = parser.getSelectParams()
    join_condition = parser.getJoinStatements(exclude_tokens=[model_name])
    where_condition = parser.whereCondition(wheres = wheres)
    table_schema, table_name = self.predictor.predict(model_name = model_name, sql = input_query, table_schema = input_schema, table_name = input_table, table_column = input_column, limit = limit)
    if table_schema is not None and table_name is not None:
      order_direction = None
      if order_by is not None:
        order_direction = parser.orderByDirection()
      sql = self.generator.scriptJoinSelectPredictOutputTable(
          select_table= table,
          select_params= selects,
          predict_table_schema=table_schema,
          predict_table_name=table_name,
          input_schema=input_schema,
          input_table=input_table,
          input_column=input_column,
          join_condition= join_condition,
          model_name=model_name,
          where_condition = where_condition,
          where_tokens = where_tokens,
          order_by = order_by,
          order_direction= order_direction,
          limit = limit
      )
      sql = self.removeWhereCondition(sql = sql, full_table_name=model_name)
      if model_name.startswith(ModelTypes.RECOMMENDER.value):
        sql = self.removeWhereCondition(sql = sql, full_table_name=table)
    return sql

  def __rewriteQueryTrain(self, sql = None):
    if sql is None:
      sql = self.sql
    parser = QueryParser(sql)
    if str(parser.getType()) != 'TRAIN':
      return sql
    if parser.parsed.subqueries_names is not None and len(parser.parsed.subqueries_names) > 0 and parser.parsed.subqueries_names[0].lower() == "training_data":
      model_name, model_type, training_data = parser.getTrainParams()
      model_id = self.trainer.train(model_name=model_name, model_type=model_type, training_data=training_data)
    return self.generator.runScriptCreateModel(model_id, model_name, model_type, training_data)

  def removeWhereCondition(self, sql = None, full_table_name = None):
    if sql is None:
      sql = self.sql
    if full_table_name == None:
      return sql
    parser = QueryParser(sql)
    schema, table, selects, join, wheres, where_tokens, offset, limit, order_by = parser.getSelectParams()
    tokens = [str(token) for token in parser.parsed.tokens]
    where_was_removed = False
    if wheres is not None and len(wheres) > 0:
      for x in range(len(tokens)):
        token = tokens[x]
        if token is not None and token.upper().replace(" ","") == "ORDERBY":
          break;
        if token is not None and str(token) in wheres:
          schema, table, column, values = parser.parseTableColumn(target = token)
          if table == full_table_name:
            if tokens[x - 1].lower() == "where":
              where_was_removed = True
            tokens[x - 1] = ""
            tokens[x] = ""
            tokens[x + 1] = ""
            tokens[x + 2] = ""
    if tokens is not None and len(tokens) > 0:
      for x in range(len(tokens)):
        if where_was_removed and (tokens[x].upper() == "AND" or tokens[x].upper() == "OR"):
          tokens[x] = "WHERE"
          break
      sql = " ".join(tokens)
    return sql