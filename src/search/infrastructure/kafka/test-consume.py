from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
from sentence_transformers import SentenceTransformer
import uuid
from os.path import exists
model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")
consumer_parse = KafkaConsumer('test_search_parse', bootstrap_servers='localhost:9092',
                               group_id='group_test', auto_offset_reset='earliest')
consumer_embed = KafkaConsumer('test_search_embed', bootstrap_servers='localhost:9092',
                               group_id='group_test_0', auto_offset_reset='earliest')
producer_embed = KafkaProducer(bootstrap_servers='localhost:9092',
                               value_serializer=lambda v: json.dumps(v).encode('utf-8'))

producer_merge = KafkaProducer(bootstrap_servers='localhost:9092',
                               value_serializer=lambda v: json.dumps(v).encode('utf-8'))

consumer_merge = KafkaConsumer('test_search_merge', bootstrap_servers='localhost:9092',
                               group_id='group_test', auto_offset_reset='earliest')
def consumeParse():
  print("start=consumeParse===============")
  for msg in consumer_parse:
    batch_id = str(uuid.uuid4())
    items = json.loads(msg.value)
    with open("{}.json".format(batch_id), "w") as outfile:
        outfile.write(json.dumps(items))
    for item in items:
      print("-------------")
      print(batch_id)
      print(item)
      future_embed = producer_embed.send('test_search_embed', {
          "_id": item["_id"],
          "source": batch_id,
          "text": item["column_value"],
      })
    future_embed.get(timeout=60)
  producer_embed.flush()
  print("end=consumeParse===============")

def consumeEmbed():
  for msg in consumer_embed:
    data = json.loads(msg.value)
    print("-------------")
    print(data)
    embedding = model.encode(data["text"])
    data["embedding"] = embedding.tolist()
    future_emerge = producer_merge.send('test_search_merge', data)
    future_emerge.get(timeout=60)
    print("-------------")
  producer_merge.flush()

def consumeMerge():
  for msg in consumer_merge:
    data = json.loads(msg.value)
    if data.get("source") is None:
      continue
    file_name = "{}.json".format(data["source"])
    if exists(file_name) is False:
      continue
    _id = data["_id"]
    items = json.load(open(file_name))
    item = [item for item in items if item.get('_id') == _id]
    if item is None or len(items) == 0:
      continue
    item = item[0]
    item["embedding"] = json.dumps(data["embedding"])
    with open(file_name, "w") as outfile:
        outfile.write(json.dumps(items))
    completed = batchHasCompleted(items)
    print(completed)

def batchHasCompleted(items):
  completed = [item for item in items if item.get('embedding') is not None]
  return len(items) == len(completed) and len(completed) > 0

consumeParse()
consumeEmbed()
consumeMerge()
'''
items = json.load(open("{}.json".format("1a90ceea-a59f-46f8-aef2-d7fc763c38da")))
print(batchHasCompleted(items))
'''