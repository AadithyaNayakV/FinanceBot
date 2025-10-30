import redis
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from redis.commands.search.query import Query

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=False)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
DIM = 384  # dimension for MiniLM-L6-v2
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

def create_redis_index():
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
            raise e

create_redis_index()

        
def data_save_in_cache(query, answer):
    vec = np.array(embedding_model.embed_query(query), dtype=np.float32).tobytes()
    key = f"cache:{hash(query)}"
    redis_client.hset(key, mapping={"vector": vec, "answer": answer})



def data_in_cache(query):
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
    return None
