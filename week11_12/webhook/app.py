"""
Webhook Provider (Flask App)
This application simulates a system that sends webhook notifications when an event occurs.
"""
from flask import Flask, request, jsonify, render_template_string
import requests
import threading
import time
import json

app = Flask(__name__)

# In-memory database for webhook subscriptions
# In a real application, you would use a persistent database (e.g., PostgreSQL, Redis)
webhook_subscriptions = {
    "payment.succeeded": [],
    "payment.failed": [],
}

# --- Webhook Logic ---

def send_webhook(url, payload):
    try:
        requests.post(url, json=payload, timeout=5)
        print(f"Sent webhook to {url}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send webhook to {url}: {e}")

def notify_subscribers(event_type, data):
    if event_type not in webhook_subscriptions:
        print(f"No subscribers for event: {event_type}")
        return

    payload = {
        "event_type": event_type,
        "data": data,
        "timestamp": time.time()
    }
    for url in webhook_subscriptions[event_type]:
        # Start a new thread for each webhook to avoid blocking
        thread = threading.Thread(target=send_webhook, args=(url, payload))
        thread.start()

# --- API Endpoints ---
@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    if not data or 'url' not in data or 'event_type' not in data:
        return jsonify({"error": "Invalid request. 'url' and 'event_type' are required."}), 400

    event_type = data['event_type']
    url = data['url']

    if event_type not in webhook_subscriptions:
        return jsonify({"error": f"Event type '{event_type}' is not supported."}), 400

    if url not in webhook_subscriptions[event_type]:
        webhook_subscriptions[event_type].append(url)
        print(f"New subscription for '{event_type}' from {url}")
        return jsonify({"message": f"Successfully subscribed to '{event_type}'."}), 201
    else:
        return jsonify({"message": "URL is already subscribed."}), 200

@app.route('/trigger-event', methods=['POST'])
def trigger_event():
    event_type = request.json.get('event_type')
    if not event_type:
        return "Please provide an event type.", 400

    event_data = {
        "transaction_id": f"txn_{int(time.time())}",
        "amount": 100.00,
        "currency": "USD"
    }
    if event_type == "payment.failed":
        event_data["reason"] = "Insufficient funds"

    notify_subscribers(event_type, event_data)
    return f"Event '{event_type}' triggered. Notifications sent to subscribers."

if __name__ == '__main__':
    print("="*50)
    print("Webhook Provider Server starting on http://127.0.0.1:5001")
    print("="*50)
    app.run(port=5001, debug=True)
