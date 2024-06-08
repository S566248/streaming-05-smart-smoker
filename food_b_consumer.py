import pika
import time
from collections import deque

def food_b_callback(ch, method, properties, body):
    global food_b_window
    try:
        decoded_body = body.decode('latin-1')
        temp = float(decoded_body.split(',')[1])  # Assuming temp is the second item
        food_b_window.append(temp)
        
        if len(food_b_window) == food_b_window.maxlen:
            if max(food_b_window) - min(food_b_window) <= 1:
                print("Food B stall alert! Temperature changed less than 1°F in 10 minutes.")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='03-food-B', durable=True)

food_b_window = deque(maxlen=20)  # 10 minutes * 1 reading/0.5 minute

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='03-food-B', on_message_callback=food_b_callback)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()