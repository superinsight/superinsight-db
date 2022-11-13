from database.sql.query_parser import QueryParser
from database.sql.generator import SqlGenerator
from database.sql.rewriter import SqlRewriter

def rewrite_create_table(query, parser):
    schema, table, columns, values, tokens = parser.getCreateParams()
    query = SqlGenerator(schema_name=schema, table_name=table).runScriptCreateTableAndTrigger(query)
    return query

def rewrite_predict_query(query, db_database, db_user):
    rewriter = SqlRewriter(sql=query, db_database = db_database, db_user = db_user)
    return rewriter.rewrite()

def rewrite_train_query(query, db_database, db_user):
    rewriter = SqlRewriter(sql=query, db_database = db_database, db_user = db_user)
    return rewriter.rewrite()

def rewrite_query(query, context):
    try:
        print("rewrite_query.received:{}".format(query))
        db_user = context["connect_params"]["user"]
        db_database = context["connect_params"]["database"]
        print("rewrite_query.db_user:{}".format(db_user))
        print("rewrite_query.db_database:{}".format(db_database))
        parser = QueryParser(query)
        print("parser.isValid():{}".format(parser.isValid()))
        if parser.isValid() == True:
            print("parser.getType():{}".format(parser.getType()))
            if str(parser.getType()) == 'CREATE':
                query = rewrite_create_table(query, parser)
            if str(parser.getType()) == 'PREDICT':
                query = rewrite_predict_query(query, db_database, db_user)
            if str(parser.getType()) == 'TRAIN':
                query = rewrite_train_query(query, db_database, db_user)
        print("rewrite_query.returns:{}".format(query))
        return query
    except Exception as e:
        print("rewrite_query.exceoption.returns:{}".format(query))
        print(e)
        return query
      

