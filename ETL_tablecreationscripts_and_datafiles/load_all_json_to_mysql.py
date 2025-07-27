import json
import os
import mysql.connector

# === CONFIG ===
data_dir = r"D:\Data Engineering Course\Final_Capstone_project\ETLrelated_datafiles"
file_table_map = {
    "delivery_fulltable.json": "delivery",
    "inventory_fulltable.json": "inventory",
    "masterdata_fulltable.json": "masterdata",
    "orders_fulltable.json": "orders"
}

# === MySQL Connection ===
conn = mysql.connector.connect(
    host="localhost",  # or docker service name
    user="root",
    password="your_mysql_password",
    database="ETL"
)
cursor = conn.cursor()

# === Data Loader ===
for file_name, table_name in file_table_map.items():
    file_path = os.path.join(data_dir, file_name)
    print(f"\n🔄 Loading {file_name} into `{table_name}`...")

    with open(file_path, 'r') as f:
        records = json.load(f)

    if not records:
        print(f"⚠️  No data found in {file_name}")
        continue

    columns = records[0].keys()
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    data = [tuple(record[col] if record[col] != "" else None for col in columns) for record in records]

    cursor.executemany(insert_sql, data)
    conn.commit()
    print(f"✅ Inserted {cursor.rowcount} rows into `{table_name}`")

# === Done ===
cursor.close()
conn.close()
print("\n🎉 All tables loaded successfully.")
