from kafka import KafkaProducer
import json
producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


def testProduceDataset():
	future = producer.send('test_search_parse', 	{
            "_id": [1, 2, 3],
            "database": ["demo", "demo", "demo"],
        				"table_schema": ["mldb", "mldb", "mldb"],
        				"table_name": ["post_comment", "post_comment", "post_comment"],
        				"primary_key_name": ["_id", "_id", "_id"],
        				"primary_key_value": ["1", "2", "3"],
        				"column_name": ["message", "message", "message"],
        				"column_value": ["最近發現一個股票分析師，太準了\n捷徑股票  上周賺了30趴", "想了解", "買你們的基金現已虧快二十萬了,怎麼辦才好"],
        				"operation": ["INSERT", "INSERT", "INSERT"],
        				"created_on": ["2022-09-01T02:01:52.100Z", "2022-09-01T02:02:52.590Z", "2022-09-01T02:02:52.948Z"]
	})
	future.get(timeout=60)
	producer.flush()


def testProduceJson():
  json_string = """[{"_id":1,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":1,"column_name":"title","column_value":"The Shawshank Redemption","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":2,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":1,"column_name":"genre","column_value":"Drama","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":3,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":1,"column_name":"overview","column_value":"Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":4,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":2,"column_name":"title","column_value":"The Godfather","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":5,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":2,"column_name":"genre","column_value":"Crime, Drama","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":6,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":2,"column_name":"overview","column_value":"An organized crime dynasty's aging patriarch transfers control of his clandestine empire to his reluctant son.","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":7,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":3,"column_name":"title","column_value":"The Dark Knight","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":8,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":3,"column_name":"genre","column_value":"Action, Crime, Drama","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":9,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":3,"column_name":"overview","column_value":"When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.","operation":"INSERT","":"2022-08-13 04:36:40"},{"_id":10,"database":"demo","index_id":"abc123","primary_key_name":"_id","primary_key_value":4,"column_name":"title","column_value":"The Godfather: Part II","operation":"INSERT","":"2022-08-13 04:36:40"}]"""
  print(json_string)
  future = producer.send('superinsight_ml_search_divide_v0', json.loads(json_string))
  future.get(timeout=60)
  producer.flush()

testProduceJson()
