import threading
import time
import requests as http_requests

import pika
import json
from flask import Flask, request,jsonify
from config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, EXCHANGE_NAME, QUEUE_NAME, ROUTING_KEY
)

from db import get_connection, create_table

app = Flask(__name__)

def publish_to_rabbitmq(message):
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
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    
    connection.close()

@app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    item_name = data.get('item')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (item, status) VALUES (?, ?)", (item_name, 'pending')
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()

    publish_to_rabbitmq({'id':inserted_id, 'item':item_name})

    return jsonify({}), 202

@app.route('/concurrent', methods=['GET'])
def concurrent_requests():
    delay_value = request.args.get('delay_value')
    url = f'https://httpbin.org/delay/{delay_value}'
    results = []

    def fetch(url):
        response = http_requests.get(url)
        results.append(results.status_code)

    start_time = time.time()

    threads = []
    for i in range(5):
        t = threading.Thread(target=fetch, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    return jsonify({'time_taken': time_taken}), 200

if __name__ == '__main__':
    create_table()
    app.run(debug=True)


    
