from kafka.admin import KafkaAdminClient, NewTopic

admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092")

topic_list = [
    NewTopic(name="order", num_partitions=1, replication_factor=1),
    NewTopic(name="delivery", num_partitions=1, replication_factor=1)
]
admin_client.create_topics(new_topics=topic_list, validate_only=False)
print("Kafka topics created successfully.")