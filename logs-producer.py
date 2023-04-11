import pika
from server import channel

    
# déclaration de l'échange de type topic
channel.exchange_declare(exchange='logs-exchange', exchange_type='topic')

# Déclarer la file d'attente queue-data-lake
channel.queue_declare(queue='queue-data-lake')
channel.queue_bind(exchange='logs-exchange', queue='queue-data-lake', routing_key='logs')

# Déclarer la file d'attente queue-data-clean
channel.queue_declare(queue='queue-data-clean')
channel.queue_bind(exchange='logs-exchange', queue='queue-data-clean', routing_key='logs')

# ouverture du fichier de logs
with open('assets/web-server-nginx.log', 'r') as f:
    for line in f:
        # publication de chaque ligne dans l'échange
        channel.basic_publish(exchange='logs-exchange', routing_key='logs', body=line)




