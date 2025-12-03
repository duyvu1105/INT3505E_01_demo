import pika
import json
import time

def main():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"--> RabbitMQ connection failed: {e}")
        print("--> Please ensure RabbitMQ is running and restart this consumer.")
        return

    # Declare the same fanout exchange the producer is using
    exchange_name = 'order_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    # Note that the queue name is different from the notification consumer's queue.
    queue_name = 'inventory_queue'
    result = channel.queue_declare(queue=queue_name, exclusive=True)
    
    channel.queue_bind(exchange=exchange_name, queue=result.method.queue)

    print(f"Waiting for messages in [{queue_name}]. To exit press CTRL+C")

    def callback(ch, method, properties, body):
        """
        This function is called whenever a message is received from the queue.
        """
        message = json.loads(body)
        print(f"\n[x] Received {json.dumps(message)}")
        
        # Simulate processing the event
        if message.get("event_type") == "order.created":
            item = message.get("data", {}).get("item")
            quantity = message.get("data", {}).get("quantity", 0)
            if item:
                print(f"  -> Simulating inventory update for item '{item}' (quantity: -{quantity})...")
                # Simulate database/I/O work
                time.sleep(0.5) 
                print("  -> Inventory updated.")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Start consuming messages
    channel.basic_consume(
        queue=result.method.queue,
        on_message_callback=callback,
        auto_ack=False
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(" -> Stopping consumer.")
        channel.stop_consuming()
    finally:
        connection.close()
        print(" -> RabbitMQ connection closed.")

if __name__ == '__main__':
    print("="*50)
    print("Inventory Consumer")
    print("="*50)
    main()
