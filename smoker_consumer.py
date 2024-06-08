import pika
import time
from collections import deque

def smoker_callback(ch, method, properties, body):
    global smoker_window
    try:
        # Decode using 'latin-1' to handle non-UTF-8 bytes
        decoded_body = body.decode('latin-1')
        temp = float(decoded_body.split(',')[1])  # Assuming temp is the second item
        smoker_window.append(temp)
        
        if len(smoker_window) == smoker_window.maxlen:
            if smoker_window[0] - smoker_window[-1] >= 15:
                print("Smoker alert! Temperature dropped by 15°F or more in 2.5 minutes.")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='01-smoker', durable=True)

smoker_window = deque(maxlen=5)  # 2.5 minutes * 1 reading/0.5 minute

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='01-smoker', on_message_callback=smoker_callback)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()