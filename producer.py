from ensurepip import bootstrap
import json
import time

from kafka import KafkaProducer, producer

''' KAFKA_TOPIC определяет имя топика, в котором будут храниться сообщения
'''

KAFKA_TOPIC = "client_orders"
MESSAGE_LIMIT = 10

producer = KafkaProducer(bootstrap_servers="localhost:9092")

print("Going to be generate message after 10 seconds")
print("Will generate one unique message every 10 seconds")

for i in range(1, MESSAGE_LIMIT):
    data = {"order_id": i, "user_id": f"client_{i}", "items": "coffee, sandwich"}

    ''' KAFKA_TOPIC - имя топика, в который помещается сообщение data
    '''
    #serialize json message
    producer.send(KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
    print(f"Producer sent message {i} to topic " + str(KAFKA_TOPIC))
    time.sleep(10)
