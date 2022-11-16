import json
import logging
from ml.pipeline.embed import EmbedPipeline
from ml.pipeline.faiss import FaissPipeline

def enqueueItems(default_storage, database, index_id, items):
	for item in items:
		text_embedding, context_embedding, label_embedding, text_generated, labels_generated = EmbedPipeline().encode(text = item["column_value"])
		item["database"] = database
		item["index_id"] = index_id
		item["text_embedding"] = text_embedding
		item["embedding"] = json.dumps(text_embedding.tolist())
		item["context_embedding"] = json.dumps(context_embedding.tolist())
		item["label_embedding"] = json.dumps(label_embedding.tolist())
		FaissPipeline(storage_location=default_storage).write(database,index_id, items)