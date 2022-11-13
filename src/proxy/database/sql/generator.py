from common.model_types import ModelTypes
from database.sql.query_parser import QueryParser
class SqlGenerator:

	system_schema_name = "system" 
	model_schema_name = "model"
	mldb_schema_name = "mldb"
	inputs_name = "inputs" 
	table_create_write_trigger = 'table_create_write_trigger'
	schema_name = None
	table_name = None

	def __init__(self, schema_name = None, table_name = None):
		self.schema_name = schema_name
		self.table_name = table_name

	def runScriptCreateTableAndTrigger(self, sql):
		statement = sql 
		if self.schema_name is not None and self.table_name is not None:
			statement = '''
			SELECT "{}".{}('{}','{}','{}') as CREATE_TABLE_OPERATION_RETURNS;
			'''.format(self.system_schema_name, self.table_create_write_trigger, self.schema_name, self.table_name, sql)
		return statement


	def scriptJoinSelectPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, join_condition, model_name, where_condition, where_tokens, order_by, order_direction, limit):
		if model_name.startswith(ModelTypes.RECOMMENDER.value):
			return self._scriptJoinSelectPredictOutputTableForRecommender(select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, join_condition, model_name, where_condition, where_tokens, order_by, order_direction, limit)
		else:
			return self._scriptJoinSelectPredictOutputTable(select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, join_condition, model_name, where_condition, order_by, order_direction, limit)

	def _scriptJoinSelectPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, join_condition, model_name, where_condition, order_by, order_direction, limit):
		sql = "SELECT {} FROM {}.{} join {}.{} as predictions on predictions.{} = {}.{}.{}::text {}".format(",".join(select_params), self.mldb_schema_name, select_table, predict_table_schema, predict_table_name, self.inputs_name, input_schema, input_table, input_column, join_condition)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		return sql

	def _scriptJoinSelectPredictOutputTableForRecommender(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, join_condition, model_name, where_condition, where_tokens, order_by, order_direction, limit):
		item_column = None
		for token in where_tokens:
			if token[1].lower() == "model.recommender.item_id":
				schema, table, column, values = QueryParser().parseTableColumn(target = token[3])
				item_column = column
		if item_column is None:
			return sql
		sql ="SELECT DISTINCT on (predictions.user_id, predictions.item_id, predictions.score) {} FROM {}.{} predictions JOIN {}.{} ON {}.{}.{}::text = predictions.item_id::text {}".format(",".join(select_params), predict_table_schema, predict_table_name, self.mldb_schema_name, select_table, self.mldb_schema_name, select_table, item_column, join_condition)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		return sql

	def runScriptCreateModel(self, model_id, model_name, model_type, training_data):
		sql = """select '{}' as model_id,  '{}' as model_name, '{}' as model_type, '{}' as training_data, 'initializing' as status""".format(model_id, model_name, model_type, training_data.replace("'","''"))
		return sql