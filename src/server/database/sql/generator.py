from environment import Environment
from common.model_types  import ModelTypes
class SqlGenerator:

	system_schema_name = "system"
	mldb_schema_name = Environment.mldb_schema_name
	model_schema_name =Environment.model_schema_name
	system_table_name_table_logs = 'table_logs'
	system_table_name_table_logs_trigger_func = 'table_logs_trigger_func'
	table_create_write_trigger = 'table_create_write_trigger'
	schema_name = None
	table_name = None
	text_generation_inputs_name = Environment.text_generation_inputs_name
	question_answering_inputs_name = Environment.question_answering_inputs_name
	summarization_inputs_name = Environment.summarization_inputs_name
	translation_inputs_name = Environment.translation_inputs_name
	semantic_search_inputs_name = Environment.semantic_search_inputs_name
	recommender_inputs_name = Environment.recommender_inputs_name

	def __init__(self, schema_name = None, table_name = None):
		self.schema_name = schema_name
		self.table_name = table_name

	def scriptDropPublicSchema(self):
		sql = '''DROP SCHEMA IF EXISTS public;'''
		return sql

	def scriptCreateModelSchema(self):
		sql = '''CREATE SCHEMA IF NOT EXISTS {};'''.format(self.model_schema_name)
		return sql

	def formatLabelToColumn(self, label):
		return label.strip().replace(" ","_")

	def scriptCreateSemanticSearchOutputTable(self, predict_id = None, database_user = None):
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, "similar" TEXT, score float8); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.semantic_search_inputs_name, self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name

	def scriptCreateTextClassificationPredictOutputTable(self, predict_id = None, labels = None, database_user = None):
		scores_params = ["score_{} float8".format(self.formatLabelToColumn(x)) for x in labels]
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, {}); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.text_generation_inputs_name, ", ".join(scores_params), self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name

	def scriptCreateQuestionAnsweringPredictOutputTable(self, predict_id = None, database_user = None):
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, question TEXT, answer TEXT, score float8, "start" integer, "end" integer); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.question_answering_inputs_name, self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name


	def scriptCreateRecommenderPredictOutputTable(self, predict_id = None, database_user = None):
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, item_id TEXT, score float8); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.recommender_inputs_name, self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name

	def scriptCreateSummarizationPredictOutputTable(self, predict_id = None, database_user = None):
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, summary TEXT); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.summarization_inputs_name, self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name

	def scriptCreateTextGenerationPredictOutputTable(self, predict_id = None, database_user = None):
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, prompt TEXT, output TEXT); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.text_generation_inputs_name, self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name

	def scriptCreateTranslationPredictOutputTable(self, predict_id = None, database_user = None):
		table_name = "_predict_{}".format(predict_id)
		sql = 'CREATE TABLE {}.{} ("{}" TEXT, source_language TEXT, target_language TEXT, output TEXT); GRANT SELECT ON TABLE {}.{} TO {};'.format(self.model_schema_name, table_name, self.translation_inputs_name, self.model_schema_name, table_name, database_user)
		table_schema = self.model_schema_name
		return sql, table_schema, table_name

	def scriptInsertSemanticSearchPredictOutputTable(self, predict_id = None, input = None, similar = None, score = None):
		table_name = "_predict_{}".format(predict_id)
		sql = "INSERT INTO {}.{}(\"{}\", \"similar\", score) VALUES('{}', '{}', {});".format(self.model_schema_name, table_name, self.semantic_search_inputs_name, input.replace("'","''"), similar.replace("'","''"), score)
		return sql

	def scriptInsertTextPredictOutputTable(self, predict_id = None, text = None, params = None):
		table_name = "_predict_{}".format(predict_id)
		scores_input_params = ["score_{}".format(self.formatLabelToColumn(param[0])) for param in params]
		scores_value_params = [str(param[1]) for param in params]
		sql = "INSERT INTO {}.{}(\"{}\",{}) VALUES('{}', {});".format(self.model_schema_name, table_name, self.text_generation_inputs_name, ",".join(scores_input_params), text.replace("'","''"),",".join(scores_value_params))
		return sql

	def scriptInsertQuestionAnsweringPredictOutputTable(self, predict_id = None, input = None, question = None, answer = None, score = None, start=-1, end=-1):
		table_name = "_predict_{}".format(predict_id)
		sql = "INSERT INTO {}.{}(\"{}\", question, answer, score, \"start\", \"end\") VALUES('{}', '{}', '{}', {}, {}, {});".format(self.model_schema_name, table_name, self.question_answering_inputs_name, input.replace("'","''"), question.replace("'","''"), answer.replace("'","''"), score, start, end)
		return sql

	def scriptInsertRecommenderPredictOutputTable(self, predict_id = None, user_id = None, item_id = None, score = 0):
		table_name = "_predict_{}".format(predict_id)
		sql = "INSERT INTO {}.{}(\"{}\", item_id, score) VALUES('{}', '{}', {});".format(self.model_schema_name, table_name, self.recommender_inputs_name, user_id.replace("'","''"), item_id.replace("'","''"), score)
		return sql

	def scriptInsertSummarizationPredictOutputTable(self, predict_id = None, input = None, summary = None):
		table_name = "_predict_{}".format(predict_id)
		sql = "INSERT INTO {}.{}(\"{}\", summary) VALUES('{}', '{}');".format(self.model_schema_name, table_name, self.summarization_inputs_name, input.replace("'","''"), summary.replace("'","''"))
		return sql

	def scriptInsertTextGenerationPredictOutputTable(self, predict_id = None, input = None, prompt =None, output = None):
		table_name = "_predict_{}".format(predict_id)
		sql = "INSERT INTO {}.{}(\"{}\", prompt, output) VALUES('{}', '{}', '{}');".format(self.model_schema_name, table_name, self.text_generation_inputs_name, input.replace("'","''"), prompt.replace("'","''"), output.replace("'","''"))
		return sql

	def scriptInsertTranslationPredictOutputTable(self, predict_id = None, input = None, source_language =None, target_language =None, output = None):
		table_name = "_predict_{}".format(predict_id)
		sql = "INSERT INTO {}.{}(\"{}\", source_language, target_language, output) VALUES('{}', '{}', '{}', '{}');".format(self.model_schema_name, table_name, self.translation_inputs_name, input.replace("'","''"), source_language.replace("'","''"), target_language.replace("'","''"), output.replace("'","''"))
		return sql

	def scriptJoinSelectPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, model_type, where_condition, order_by, order_direction, limit):
		if model_type == ModelTypes.TEXT_CLASSIFICATION.value:
			return self._scriptJoinSelectAndTextPredictOutputTable(
				select_table = select_table,
				select_params= select_params,
				predict_table_schema=predict_table_schema,
				predict_table_name=predict_table_name,
				input_schema=input_schema,
				input_table=input_table,
				input_column=input_column,
    		where_condition= where_condition,
				order_by = order_by,
				order_direction = order_direction,
				limit = limit
      )
		elif model_type == ModelTypes.QUESTION_ANSWERING.value:
			return self._scriptJoinSelectAndQuestionAnsweringPredictOutputTable(
				select_table= select_table,
				select_params= select_params,
				predict_table_schema=predict_table_schema,
				predict_table_name=predict_table_name,
				input_schema=input_schema,
				input_table=input_table,
				input_column=input_column,
    		where_condition= where_condition,
				order_by = order_by,
				order_direction = order_direction,
				limit = limit)
		elif model_type ==  ModelTypes.SUMMARIZATION.value:
			return self._scriptJoinSelectAndSummarizationPredictOutputTable(
				select_table= select_table,
				select_params= select_params,
				predict_table_schema=predict_table_schema,
				predict_table_name=predict_table_name,
				input_schema=input_schema,
				input_table=input_table,
				input_column=input_column,
    		where_condition= where_condition,
				order_by = order_by,
				order_direction = order_direction,
				limit = limit)
		elif model_type ==  ModelTypes.TEXT_GENERATION.value:
			return self._scriptJoinSelectAndTextGenerationPredictOutputTable(
				select_table= select_table,
				select_params= select_params,
				predict_table_schema=predict_table_schema,
				predict_table_name=predict_table_name,
				input_schema=input_schema,
				input_table=input_table,
				input_column=input_column,
    		where_condition= where_condition,
				order_by = order_by,
				order_direction = order_direction,
				limit = limit)
		elif model_type ==  ModelTypes.TRANSLATION.value:
			return self._scriptJoinSelectAndTranslationPredictOutputTable(
				select_table= select_table,
				select_params= select_params,
				predict_table_schema=predict_table_schema,
				predict_table_name=predict_table_name,
				input_schema=input_schema,
				input_table=input_table,
				input_column=input_column,
    		where_condition= where_condition,
				order_by = order_by,
				order_direction = order_direction,
				limit = limit)
		else:
			return None

	def _scriptJoinSelectAndTextPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, where_condition, order_by, order_direction, limit):
		sql = "SELECT {} FROM {}.{} join {}.{} as predictions on predictions.{} = {}.{}.{}".format(",".join(select_params), self.mldb_schema_name, select_table, predict_table_schema, predict_table_name, self.text_generation_inputs_name, input_schema, input_table, input_column)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		print(sql)
		return sql 

	def _scriptJoinSelectAndQuestionAnsweringPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, where_condition, order_by, order_direction, limit):
		sql = "SELECT {} FROM {}.{} join {}.{} as predictions on predictions.{} = {}.{}.{}".format(",".join(select_params), self.mldb_schema_name, select_table, predict_table_schema, predict_table_name, self.question_answering_inputs_name, input_schema, input_table, input_column)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		print(sql)
		return sql 

	def _scriptJoinSelectAndSummarizationPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, where_condition, order_by, order_direction, limit):
		sql = "SELECT {} FROM {}.{} join {}.{} as predictions on predictions.{} = {}.{}.{}".format(",".join(select_params), self.mldb_schema_name, select_table, predict_table_schema, predict_table_name, self.summarization_inputs_name, input_schema, input_table, input_column)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		print(sql)
		return sql 

	def _scriptJoinSelectAndTextGenerationPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, where_condition, order_by, order_direction, limit):
		sql = "SELECT {} FROM {}.{} join {}.{} as predictions on predictions.{} = {}.{}.{}".format(",".join(select_params), self.mldb_schema_name, select_table, predict_table_schema, predict_table_name, self.text_generation_inputs_name, input_schema, input_table, input_column)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		print(sql)
		return sql 

	def _scriptJoinSelectAndTranslationPredictOutputTable(self, select_table, select_params, predict_table_schema, predict_table_name, input_schema, input_table, input_column, where_condition, order_by, order_direction, limit):
		sql = "SELECT {} FROM {}.{} join {}.{} as predictions on predictions.{} = {}.{}.{}".format(",".join(select_params), self.mldb_schema_name, select_table, predict_table_schema, predict_table_name, self.translation_inputs_name, input_schema, input_table, input_column)
		if where_condition is not None:
			sql = "{} {}".format(sql, where_condition)
		if order_by is not None:
			if order_direction is None:
				order_direction = "ASC"
			sql = "{} order by {} {}".format(sql, " ".join(order_by), order_direction)
		if limit is not None:
			sql = "{} LIMIT {}".format(sql, limit)
		print(sql)
		return sql 
	def scriptCreateMldbSchema(self):
		sql = '''CREATE SCHEMA IF NOT EXISTS {};'''.format(self.mldb_schema_name)
		return sql

	def scriptCreateSystemSchema(self):
		sql = '''CREATE SCHEMA IF NOT EXISTS {};'''.format(self.system_schema_name)
		return sql

	def scriptCreateSystemLogTable(self):
		sql = '''CREATE SCHEMA IF NOT EXISTS {};
  CREATE TABLE IF NOT EXISTS {}.{} (
	_id serial PRIMARY KEY,
	table_schema VARCHAR ( 255 ) NOT NULL,
	table_name VARCHAR ( 255 ) NOT NULL,
	primary_key_name TEXT,
	primary_key_value TEXT,
	column_name VARCHAR ( 255 ) NOT NULL,
	column_value TEXT,
	operation VARCHAR ( 255 ) NOT NULL,
	created_on TIMESTAMP NOT NULL);'''.format(self.system_schema_name, self.system_schema_name, self.system_table_name_table_logs)
		return sql

	def scriptCreateLogTableTriggerFunction(self):
		sql = '''CREATE OR REPLACE FUNCTION {}.{}()
  RETURNS trigger as
	$$
	declare
			valid_col record;
			primary_col text;
	BEGIN
		SELECT a.attname
		into primary_col
		FROM   pg_index i
		JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
		WHERE  i.indrelid = concat(TG_TABLE_SCHEMA,'.',TG_TABLE_NAME)::regclass
		AND    i.indisprimary limit 1;
		FOR valid_col in SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_schema = TG_TABLE_SCHEMA AND table_name = TG_TABLE_NAME AND data_type= 'text'
		loop
			if TG_OP = 'INSERT' or TG_OP = 'UPDATE' then
				EXECUTE 'INSERT INTO {}.{} (table_schema,table_name,column_name,operation,primary_key_name,primary_key_value,column_value,created_on) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)' USING TG_TABLE_SCHEMA, TG_TABLE_NAME, valid_col.column_name, TG_OP,primary_col, (select json_extract_path_text(row_to_json(NEW),primary_col))::text, (select json_extract_path_text(row_to_json(NEW),valid_col.column_name)),current_timestamp;
				END if;
			if TG_OP = 'DELETE' or TG_OP = 'TRUNCATE' then
					EXECUTE 'INSERT INTO {}.{} (table_schema,table_name,column_name,operation,primary_key_name,primary_key_value,column_value,created_on) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)' USING TG_TABLE_SCHEMA, TG_TABLE_NAME, valid_col.column_name, TG_OP,primary_col, (select json_extract_path_text(row_to_json(OLD),primary_col))::text, (select json_extract_path_text(row_to_json(NEW),valid_col.column_name)),current_timestamp;
			END if;
	END LOOP; 
    if TG_OP = 'INSERT' or TG_OP = 'UPDATE' then
		  RETURN NEW;
	  END if;
   	if TG_OP = 'DELETE' or TG_OP = 'TRUNCATE' then
   		RETURN OLD;
   	END if;
	END;
	$$
	LANGUAGE 'plpgsql';'''.format(self.system_schema_name, self.system_table_name_table_logs_trigger_func, self.system_schema_name, self.system_table_name_table_logs, self.system_schema_name, self.system_table_name_table_logs)
		return sql

	def scriptWriteLogTrigger(self):
		sql = '''CREATE OR REPLACE FUNCTION {}.{}(table_schema TEXT, table_name TEXT, sql TEXT)
			RETURNS INTEGER as
			$$
			declare
				trigger_before text;
				trigger_after text;
			begin

			--RUN CREATE TABLE
			execute sql;

			--ADD TRIGGERS
			trigger_before = 'CREATE OR REPLACE TRIGGER _trigger_logs_before
			BEFORE DELETE
			ON ' || table_schema || '.' || table_name || '
			FOR EACH ROW
			EXECUTE PROCEDURE {}.{}();';
			execute trigger_before;

			trigger_after = 'CREATE OR REPLACE TRIGGER _trigger_logs_after
			AFTER INSERT or UPDATE
			ON ' || table_schema || '.' || table_name || '
			FOR EACH ROW
			EXECUTE PROCEDURE {}.{}();';
			execute trigger_after;

			return 1;

			END;
			$$ LANGUAGE plpgsql;
		'''.format(self.system_schema_name, self.table_create_write_trigger,self.system_schema_name, self.system_table_name_table_logs_trigger_func, self.system_schema_name, self.system_table_name_table_logs_trigger_func)
		return sql

	def runScriptCreateTableAndTrigger(self, sql):
		statement = sql 
		if self.schema_name is not None and self.table_name is not None:
			statement = '''
			SELECT "{}".{}('{}','{}','{}') as CREATE_TABLE_OPERATION_RETURNS;
			'''.format(self.system_schema_name, self.table_create_write_trigger, self.schema_name, self.table_name, sql)
		return statement