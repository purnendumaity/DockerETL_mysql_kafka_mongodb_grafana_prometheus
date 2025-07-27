from pymongo import MongoClient
import mysql.connector
import datetime

# MongoDB connection
mongo_client = MongoClient('mongodb://root:pass@mongodb:27017/')
mongo_db = mongo_client['ETL']
mongo_collection = mongo_db['inventory']

# MySQL connection
mysql_conn = mysql.connector.connect(
    host='mysql',
    user='root',
    password='pass',
    database='ETL'
)
mysql_cursor = mysql_conn.cursor()

def load_inventory_from_mongo():
    print("🚀 Starting inventory load from MongoDB")

    documents = list(mongo_collection.find())
    print(f"📦 Found {len(documents)} records in MongoDB inventory")

    insert_query = """
        INSERT INTO inventory (
            product_id, warehouse_id, product_name,
            product_category, stock_level,
            last_order_qty, remain_inventory, Last_updatetime
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    inserted_count = 0
    for doc in documents:
        record = (
            doc.get("product_id"),
            doc.get("warehouse_id"),
            doc.get("product_name"),
            doc.get("product_category"),
            doc.get("stock_level"),
            0,  # last_order_qty
            0,  # remain_inventory
            None  # Last_updatetime
        )
        try:
            mysql_cursor.execute(insert_query, record)
            inserted_count += 1
        except Exception as e:
            print(f"❌ Insert error for record {record}: {e}")

    mysql_conn.commit()
    print(f"✅ Inserted {inserted_count} inventory records into MySQL")

    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()
    print("✅ Task1 of ETL Inventory load completed")