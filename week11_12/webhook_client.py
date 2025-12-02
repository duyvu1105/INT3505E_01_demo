"""
Webhook Client (Flask App)
This application acts as a client that subscribes to and receives webhooks.
"""
from flask import Flask, request, jsonify, render_template_string
import requests
import json

app = Flask(__name__)

# In-memory log of received webhooks
# In a real application, you might store this in a file or database
received_webhooks = []

# --- Configuration ---
# The URL of the webhook provider
PROVIDER_URL = "http://127.0.0.1:5001"
# The URL this client exposes to receive webhooks
# NOTE: In a real-world scenario, this must be a publicly accessible URL.
# We use http://127.0.0.1 here for local demonstration.
CLIENT_WEBHOOK_URL = "http://127.0.0.1:5002/webhook-receiver"

# --- Client Logic ---
@app.route('/subscribe', methods=['POST'])
def subscribe_to_event():
    """
    Sends a subscription request to the webhook provider.
    """
    data = request.get_json()
    event_type = data.get('event_type') if data else None
    if not event_type:
        return "Error: No event type specified.", 400

    subscription_payload = {
        "event_type": event_type,
        "url": CLIENT_WEBHOOK_URL
    }

    try:
        response = requests.post(f"{PROVIDER_URL}/subscribe", json=subscription_payload)
        response.raise_for_status() # Raise an exception for bad status codes
        message = response.json().get("message", "Subscription successful.")
    except requests.exceptions.RequestException as e:
        message = f"Error subscribing: {e}"

    return f"Subscription attempt for '{event_type}': {message}"


@app.route('/webhook-receiver', methods=['POST'])
def webhook_receiver():
    """
    The endpoint that receives the actual webhook notifications from the provider.
    """
    if request.is_json:
        data = request.get_json()
        print(f"Received webhook: {json.dumps(data, indent=2)}")
        
        # Add the received webhook to our in-memory log
        received_webhooks.append(data)
        
        # It's a best practice to respond quickly with a 2xx status code
        # to let the provider know you've received the webhook.
        # Any complex processing should be done asynchronously (e.g., in a background queue).
        return jsonify({"status": "received"}), 200
    else:
        return "Request was not JSON", 400


@app.route('/webhooks', methods=['GET'])
def webhooks():
    """
    Displays the log of received webhooks.
    """
    # Sort webhooks by timestamp, newest first
    return jsonify(received_webhooks)

if __name__ == '__main__':
    print("="*50)
    print("Webhook Client Server starting on http://127.0.0.1:5002")
    print(f"Listening for webhooks at: {CLIENT_WEBHOOK_URL}")
    print("="*50)
    app.run(port=5002, debug=True)
