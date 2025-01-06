# Crates a collection called profiles1
# Modified based on the example python file

from pymilvus import MilvusClient, DataType
import configparser
import json

# Read credentials 
cfp = configparser.RawConfigParser()
cfp.read('config.ini')
milvus_uri = cfp.get('default', 'uri')
token = cfp.get('default', 'token')
milvus_client = MilvusClient(uri=milvus_uri, token=token)
print(f"Connected to DB: {milvus_uri}")

# If the collection already exits, drop it
collection_name = "profiles1"
check_collection = milvus_client.has_collection(collection_name)
if check_collection:
    milvus_client.drop_collection(collection_name)
    print("Dropped the existing collection")
    
# preparing schema
dim = 1536
schema = milvus_client.create_schema()
schema.add_field("Name", DataType.VARCHAR, is_primary = True, 
                 description = "Primary Key: Name", max_length = 100)
schema.add_field("Embedding", DataType.FLOAT_VECTOR, dim= dim, 
                 description = "About section in vector form")

# adds index 
index_params = milvus_client.prepare_index_params()
index_params.add_index("Embedding", metric_type="COSINE")
print("Index created")

# create collection
milvus_client.create_collection(collection_name, dim, schema=schema, index_params=index_params)
collection_property = milvus_client.describe_collection(collection_name)
print("Show collection details: %s" % collection_property)

# insert data from modified_out.json
