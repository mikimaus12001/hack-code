import json
from kafka import KafkaConsumer

# *topics (str)
consumer = KafkaConsumer("client_orders", bootstrap_servers="localhost:9092")

# в файле consumer.py в цикле выводим на экран сообщения, которые получил Kafka Consumer
for message in consumer:
    print(json.loads(message.value))