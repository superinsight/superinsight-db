from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from typing import List
from common.storage_location import StorageLocation
import os, sys
from ml.pipeline.faiss import FaissPipeline
from ml.pipeline.embed import EmbedPipeline
import json
app = FastAPI()
version = "0.9.1"
os.environ["KMP_DUPLICATE_LIB_OK"]="True"

@app.on_event("startup")
async def startup_event():
    print("app startup")

@app.get("/")
async def read_root():
    return {"version": version}

class SearchRequest(BaseModel):
    context: str = None
    size: int = 10
    primary_key_values: List[str] = None

class CreateRequestItem(BaseModel):
    _id: int 
    primary_key_name: str 
    primary_key_value: str 
    column_name: str 
    column_value: str 
    operation: str 

class CreateRequest(BaseModel):
    items: List[dict] = []

default_storage = StorageLocation.LOCAL_DISK

@app.post("/{database}/{index_id}/_search")
async def search(database: str, index_id: str, req: SearchRequest):
    try:
      predictions = []
      pipeline = FaissPipeline(storage_location=default_storage)
      predictions = pipeline.search(database=database, index_id=index_id, context=req.context, limit=req.size, primary_key_values=req.primary_key_values)
      return { "predictions": predictions}
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return { "predictions": [] }

@app.get("/{database}/{index_id}/_count")
async def count(database: str, index_id: str):
    try:
      pipeline = FaissPipeline(storage_location=default_storage)
      count = pipeline.count(database=database, index_id=index_id)
      return { "count": count }
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return { "count": 0 }

@app.post("/{database}/{index_id}/")
async def create(database: str, index_id: str, req: CreateRequest):
    try:
      items = req.items
      for item in req.items:
        print(item)
        text_embedding, context_embedding, label_embedding, text_generated, labels_generated = EmbedPipeline().encode(text = item["column_value"])
        print(text_embedding, context_embedding, label_embedding, text_generated, labels_generated)
        item["database"] = database
        item["index_id"] = index_id
        item["text_embedding"] = text_embedding
        item["embedding"] = json.dumps(text_embedding.tolist())
        item["context_embedding"] = json.dumps(context_embedding.tolist())
        item["label_embedding"] = json.dumps(label_embedding.tolist())
      FaissPipeline(storage_location=default_storage).write(database,index_id, items)
      return { "status": "created"}
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return { "status": "failed"}