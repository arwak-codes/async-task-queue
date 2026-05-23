import pika
import json
from celery import Celery
from config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, QUEUE_NAME, EXCHANGE_NAME, ROUTING_KEY
)
from db import get_connection

BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'

celery_app = Celery('worker', broker=BROKER_URL)

@celery_app.task(name=QUEUE_NAME)
def process_item(item_id, item_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE items SET status = 'completed' WHERE id = ? AND status = 'pending'", (item_id,)
    )
    conn.commit()
    conn.close()
    print(f"Processed item '{item_name}' with id {item_id} → completed")

def start_consumer():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host = RABBITMQ_HOST,
            port = RABBITMQ_PORT,
            credentials = credentials
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct', durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        item_id = message.get('id')
        item_name = message.get('item')
        print(f"Received: {message}")
        process_item(item_id, item_name)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print('Worker is running. Waiting for messages...')
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()



