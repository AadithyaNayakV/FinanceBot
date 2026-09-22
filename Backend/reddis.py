import redis
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from redis.commands.search.query import Query
import os

REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "default")
REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() == "true"

redis_client = None
try:
    if REDIS_URL:
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=False)
    elif REDIS_PASSWORD:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            ssl=REDIS_SSL,
            decode_responses=False,
            socket_timeout=5
        )
    else:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False, socket_timeout=5)
    
    redis_client.ping()
    print("Redis connected successfully ✅")
except Exception as e:
    print(f"⚠️ Redis connection warning: {e}. Running without Redis cache.")
    redis_client = None

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
DIM = 384  # dimension for MiniLM-L6-v2
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType

def create_redis_index():
    if not redis_client:
        return
    try:
        redis_client.ft("cache_index").create_index(
            [
                VectorField("vector", "FLAT", {
                    "TYPE": "FLOAT32",
                    "DIM": DIM,
                    "DISTANCE_METRIC": "COSINE"
                }),
                TextField("answer")
            ],
            definition=IndexDefinition(prefix=["cache:"], index_type=IndexType.HASH)
        )
        print("Redis vector index created ✅")
    except Exception as e:
        if "Index already exists" in str(e):
            pass  # ignore
        else:
            print(f"⚠️ Redis vector index warning: {e}")

create_redis_index()

        
def data_save_in_cache(query, answer):
    if not redis_client:
        return
    try:
        vec = np.array(embedding_model.embed_query(query), dtype=np.float32).tobytes()
        key = f"cache:{hash(query)}"
        if redis_client.exists(key):
            return  
        else:
            redis_client.hset(key, mapping={"vector": vec, "answer": answer})
    except Exception as e:
        print(f"⚠️ Failed to cache in Redis: {e}")



def data_in_cache(query):
    if not redis_client:
        return None
    try:
        vec = np.array(embedding_model.embed_query(query), dtype=np.float32).tobytes()
        q = (
            Query("*=>[KNN 1 @vector $vec AS score]")
            .sort_by("score")
            .return_fields("answer", "score")
            .dialect(2)
        )

        results = redis_client.ft("cache_index").search(q, query_params={"vec": vec})
        if results.docs:
            score = float(results.docs[0].score)
            if score < 0.2:  # adjust threshold for similarity
                return results.docs[0].answer
    except Exception as e:
        print(f"⚠️ Redis search error: {e}")
    return None
