import pika
import time
from collections import deque

def food_a_callback(ch, method, properties, body):
    global food_a_window
    try:
        decoded_body = body.decode('latin-1')
        temp = float(decoded_body.split(',')[1])  # Assuming temp is the second item
        food_a_window.append(temp)
        
        if len(food_a_window) == food_a_window.maxlen:
            if max(food_a_window) - min(food_a_window) <= 1:
                print("Food A stall alert! Temperature changed less than 1°F in 10 minutes.")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='02-food-A', durable=True)

food_a_window = deque(maxlen=20)  # 10 minutes * 1 reading/0.5 minute

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='02-food-A', on_message_callback=food_a_callback)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()