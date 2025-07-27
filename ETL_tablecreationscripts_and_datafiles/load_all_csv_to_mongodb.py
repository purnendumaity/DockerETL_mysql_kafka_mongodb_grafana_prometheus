import pandas as pd
from pymongo import MongoClient

# === CONFIG ===
csv_path = r"D:\Data Engineering Course\Final_Capstone_project\ETLrelated_datafiles\mongodb_inventory.csv"
mongo_uri = "mongodb://localhost:27017/"  # change to your Mongo container URI if needed
mongo_db = "ETL"
mongo_collection = "inventory"

# === LOAD CSV ===
df = pd.read_csv(csv_path)

# Replace empty strings with None (Mongo stores as null)
df = df.where(pd.notnull(df), None)

# Convert dataframe to dict records
records = df.to_dict(orient='records')

# === INSERT INTO MONGODB ===
client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

# Optional: clear existing collection
collection.delete_many({})

# Insert all records
result = collection.insert_many(records)
print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB `{mongo_db}.{mongo_collection}`")

client.close()
