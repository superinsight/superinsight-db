import os
import glob
import uuid
from environment import Environment
import json
import logging
from common.storage_location import StorageLocation
from ml.pipeline.embed import EmbedPipeline
from ml.pipeline.faiss import FaissPipeline


class DatabaseQueue:

    faiss_pipeline = None
    logger = logging.getLogger(Environment.logger_name)
    logger.setLevel(logging.INFO)

    def enqueue(self, database, index_id, items):
        directory = "{}/.processing/{}/{}".format(
            Environment.default_storage, database, index_id
        )
        if not os.path.exists(directory):
            os.makedirs(directory)
        for item in items:
            process_id = str(uuid.uuid4())
            item["database"] = database
            item["index_id"] = index_id
        target_path = "{}/{}.json".format(directory, process_id)
        with open(target_path, "w") as outfile:
            outfile.write(json.dumps(items))

    def dequeue(self, storage_location=StorageLocation.MEMORY_CACHE):
        directory = "{}/.processing".format(Environment.default_storage)
        sub_directories = [x[0] for x in os.walk(directory)]
        for sub_directory in sub_directories:
            files = [f for f in glob.glob("{}/*.json".format(sub_directory))]
            for file in files:
                items = []
                items = json.load(open(file))
                database = None
                index_id = None
                for item in items:
                    (
                        text_embedding,
                        context_embedding,
                        label_embedding,
                        text_generated,
                        labels_generated,
                    ) = EmbedPipeline().encode(text=item["column_value"])
                    item["text_embedding"] = text_embedding
                    item["embedding"] = json.dumps(text_embedding.tolist())
                    item["context_embedding"] = json.dumps(context_embedding.tolist())
                    item["label_embedding"] = json.dumps(label_embedding.tolist())
                    item["text_generated"] = text_generated
                    item["labels_generated"] = labels_generated
                    database = item["database"]
                    index_id = item["index_id"]
                FaissPipeline(storage_location=storage_location).write(
                    database, index_id, items
                )
                if os.path.exists(file):
                    os.remove(file)
