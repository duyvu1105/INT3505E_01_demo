import pika
import json
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    exchange_name = 'order_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    print("--> RabbitMQ connection successful.")
except pika.exceptions.AMQPConnectionError as e:
    print(f"--> RabbitMQ connection failed: {e}")
    print("--> Please ensure RabbitMQ is running (e.g., via Docker).")
    connection = None
    channel = None


@app.route('/create_order', methods=['POST'])
def create_order():
    """
    Receives an order request, and instead of processing it,
    publishes an 'order.created' event to RabbitMQ.
    """
    if not channel:
        return jsonify({"error": "RabbitMQ service is not available."}), 503

    data = request.get_json()
    if not data or 'customer_email' not in data or 'item' not in data:
        return jsonify({"error": "Invalid order data. 'customer_email' and 'item' are required."}), 400

    # Create the event payload
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_type": "order.created",
        "data": {
            "customer_email": data['customer_email'],
            "item": data['item'],
            "quantity": data.get('quantity', 1)
        }
    }
    
    message_body = json.dumps(event_payload)

    # The routing_key is ignored for fanout exchanges, but we provide it for consistency.
    channel.basic_publish(
        exchange=exchange_name,
        routing_key='', # routing_key is not needed for fanout exchanges
        body=message_body
    )

    print(f"[x] Sent event: {event_payload['event_type']} for {data['customer_email']}")
    
    return jsonify({
        "message": "Order received and event published.",
        "event_id": event_payload['event_id']
    }), 202 # 202 Accepted: The request has been accepted for processing, but the processing has not been completed.

if __name__ == '__main__':
    if not channel:
        print("\n[ERROR] Could not connect to RabbitMQ. The producer will not be able to send messages.")
        print("Please start RabbitMQ and restart this application.\n")
    
    print("="*50)
    print("Order Producer (Flask App)")
    print(f"Listening on http://127.0.0.1:5000")
    print(f"Publishing events to exchange '{exchange_name}'")
    print("="*50)
    app.run(port=5000)

# Make sure to close the connection when the app exits
if connection:
    connection.close()
