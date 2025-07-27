from kafka import KafkaProducer, KafkaConsumer
import mysql.connector
import json
import time
import os

KAFKA_BROKER = 'kafka:9092'
ORDERS_TOPIC = 'orders_topic'
DELIVERY_TOPIC = 'delivery_topic'
INPUT_PATH = '/opt/airflow/kafka_input/'
MYSQL_CONFIG = {
    'host': 'mysql',
    'user': 'root',
    'password': 'pass',
    'database': 'ETL'
}

def produce_json_data(file_name, topic):
    path = os.path.join(INPUT_PATH, file_name)
    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {file_name}")
            return

    count = 0
    for record in data:
        producer.send(topic, record)
        count += 1

    producer.flush()
    print(f"✅ Produced {count} records to topic '{topic}'")

def consume_and_insert(topic, table_name):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=f'etl_group_{table_name}',  # Unique group for each table
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    insert_count = 0
    max_messages = 500
    max_empty_polls = 5
    empty_polls = 0

    while insert_count < max_messages and empty_polls < max_empty_polls:
        msg_pack = consumer.poll(timeout_ms=3000)

        if not msg_pack:
            empty_polls += 1
            continue

        for tp, messages in msg_pack.items():
            for message in messages:
                record = message.value
                try:
                    placeholders = ','.join(['%s'] * len(record))
                    query = f"INSERT INTO {table_name} ({', '.join(record.keys())}) VALUES ({placeholders})"
                    cursor.execute(query, list(record.values()))
                    insert_count += 1
                except Exception as e:
                    print(f"❌ Insert error for record {record}: {e}")

        conn.commit()

    print(f"✅ Inserted {insert_count} total records into {table_name}")
    cursor.close()
    conn.close()
    consumer.close()

def load_order_and_delivery_data():
    print("🚀 Starting ETL with JSON files")

    global producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Step 1: Produce Orders
    produce_json_data('orders.json', ORDERS_TOPIC)
    print("✅ Orders producer completed")

    # Step 2: Consume Orders
    consume_and_insert(ORDERS_TOPIC, 'orders')
    print("✅ Orders consumer completed")

    time.sleep(5)

    # Step 3: Produce Delivery
    produce_json_data('delivery.json', DELIVERY_TOPIC)
    print("✅ Delivery producer completed")

    # Step 4: Consume Delivery
    consume_and_insert(DELIVERY_TOPIC, 'delivery')
    print("✅ Delivery consumer completed")

    print("✅ Task2 of ETL completed")

