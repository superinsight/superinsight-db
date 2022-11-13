CREATE SCHEMA IF NOT exists system;
CREATE SCHEMA IF NOT exists mldb;
CREATE SCHEMA IF NOT exists model;
DROP SCHEMA IF EXISTS public;

CREATE TABLE IF NOT EXISTS model.semantic_search(
    inputs TEXT,
    "similar" TEXT,
    score float8
);
CREATE TABLE IF NOT EXISTS model.text_classification(
    inputs TEXT,
    labels TEXT
);
CREATE TABLE IF NOT EXISTS model.question_answering(
    inputs TEXT,
    question TEXT
);
CREATE TABLE IF NOT EXISTS model.summarization(
    inputs TEXT,
    min_length int4
);
CREATE TABLE IF NOT EXISTS model.text_generation(
    inputs TEXT,
    prompt TEXT,
    max_length int4,
    min_length int4,
    stop_word TEXT
);
CREATE TABLE IF NOT EXISTS model.translation(
    inputs TEXT,
    source_language TEXT,
    target_language TEXT
);
CREATE TABLE IF NOT EXISTS model.recommender (
	user_id TEXT,
	item_id TEXT,
	timestamp int4
);

CREATE TABLE IF NOT EXISTS system.table_logs (
	_id serial PRIMARY KEY,
	table_schema VARCHAR ( 255 ) NOT NULL,
	table_name VARCHAR ( 255 ) NOT NULL,
	primary_key_name TEXT,
	primary_key_value TEXT,
	column_name VARCHAR ( 255 ) NOT NULL,
	column_value TEXT,
	operation VARCHAR ( 255 ) NOT NULL,
	created_on TIMESTAMP NOT NULL);


CREATE OR REPLACE FUNCTION system.table_create_write_trigger(table_schema TEXT, table_name TEXT, sql TEXT)
	RETURNS INTEGER as
	$$
	declare
		trigger_before text;
		trigger_after text;
	begin
	
	--RUN CREATE TABLE
	execute sql;
	
	--ADD TRIGGERS
	trigger_before = 'CREATE TRIGGER _trigger_logs_before
	BEFORE DELETE
	ON ' || table_schema || '.' || table_name || '
	FOR EACH ROW
	EXECUTE PROCEDURE system.table_logs_trigger_func();';
	execute trigger_before;
	
	trigger_after = 'CREATE TRIGGER _trigger_logs_after
	AFTER INSERT or UPDATE
	ON ' || table_schema || '.' || table_name || '
	FOR EACH ROW
	EXECUTE PROCEDURE system.table_logs_trigger_func();';
	execute trigger_after;
	
	return 1;
	
	END;
	$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION system.table_logs_trigger_func()
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
				EXECUTE 'INSERT INTO system.table_logs (table_schema,table_name,column_name,operation,primary_key_name,primary_key_value,column_value,created_on) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)' USING TG_TABLE_SCHEMA, TG_TABLE_NAME, valid_col.column_name, TG_OP,primary_col, (select json_extract_path_text(row_to_json(NEW),primary_col))::text, (select json_extract_path_text(row_to_json(NEW),valid_col.column_name)),current_timestamp;
				END if;
			if TG_OP = 'DELETE' or TG_OP = 'TRUNCATE' then
					EXECUTE 'INSERT INTO system.table_logs (table_schema,table_name,column_name,operation,primary_key_name,primary_key_value,column_value,created_on) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)' USING TG_TABLE_SCHEMA, TG_TABLE_NAME, valid_col.column_name, TG_OP,primary_col, (select json_extract_path_text(row_to_json(OLD),primary_col))::text, (select json_extract_path_text(row_to_json(NEW),valid_col.column_name)),current_timestamp;
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
	LANGUAGE 'plpgsql';