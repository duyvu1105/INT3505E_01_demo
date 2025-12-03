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

    queue_name = 'notification_queue'
    
    result = channel.queue_declare(queue=queue_name, exclusive=True)
    
    channel.queue_bind(exchange=exchange_name, queue=result.method.queue)

    print(f"[*] Waiting for messages in [{queue_name}]. To exit press CTRL+C")

    def callback(ch, method, properties, body):
        """
        This function is called whenever a message is received from the queue.
        """
        message = json.loads(body)
        print(f"\n[x] Received {json.dumps(message)}")
        
        # Simulate processing the event
        if message.get("event_type") == "order.created":
            customer_email = message.get("data", {}).get("customer_email")
            if customer_email:
                print(f"  -> Simulating sending confirmation email to {customer_email}...")
                # Simulate I/O-bound work
                time.sleep(1) 
                print("  -> Email sent.")

        # Acknowledge the message. This tells RabbitMQ that the message has been
        # successfully received and processed, and can be safely discarded.
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Start consuming messages from the queue
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
    print("Notification Consumer")
    print("="*50)
    main()
