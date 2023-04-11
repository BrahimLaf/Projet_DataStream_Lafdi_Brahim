import hashlib
import re
import signal
import sys
from datetime import datetime
from server import channel
from models import RowLog
from main import create_database, engine, Base
from sqlalchemy.orm import sessionmaker
    
# configuration des files d'attente et de l'échange
exchange_name = 'logs-exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
queue_name = 'queue-data-lake'
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='logs')

# Récupération de la session
Session = sessionmaker(bind=engine)
session = Session()

# fonction de callback appelée lorsqu'un message est reçu
def callback(ch, method, properties, body):
    log_line = body.decode().rstrip("-\n")
    log_parts = re.split('\s+', log_line, maxsplit=9)
    ip_address = log_parts[0]
    user_id = log_parts[1]
    username = log_parts[2]

    # Extract timestamp using regular expression
    timestamp_regex = r'\[(\d{2}/\w+/\d{4}:\d{2}:\d{2}:\d{2} [-+]\d{4})\]'
    timestamp_match = re.search(timestamp_regex, log_line)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1)
        # Convert timestamp to datetime object
        timestamp_obj = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
        # Add the UTC offset to the UTC time
        timestamp_obj -= timestamp_obj.utcoffset()
        timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')

    request = re.search(r'"([^"]+)"', log_line).group(1)
    status_code = log_parts[6]
    content_length = log_parts[7]
    referer = log_parts[8]
    user_agent = log_parts[9]

    # Calculate MD5 hash of the log line
    hash_object = hashlib.md5(log_line.encode())
    log_id = hash_object.hexdigest()

    # suppression des "" de la chaîne "request"
    request = re.sub(r'(^"|"$)', '', request)

    # Insertion de la ligne de log dans la base de données
    try:
        # Ajouter les données à la base de données
        raw_log = RowLog(id=log_id, timestamp=timestamp, log=log_line) 
        # Rechercher les doublons dans la base de données
        doublon = session.query(RowLog).filter_by(id=log_id).one_or_none()
        if not doublon: 
            session.add(raw_log)
            session.commit()  # Valider la transaction
            print("Ligne de log insérée dans la base de données : " + log_line)
    except Exception as e:
        session.rollback()  # Annuler la transaction en cas d'erreur
        raise e



def signal_handler(signal, frame):
    # insérer le dernier enregistrement dans la base de données
    # fermer la session
    session.close()
    print('Programme terminé.')
    sys.exit(0)

# interception du signal SIGINT
signal.signal(signal.SIGINT, signal_handler)


# consommation des messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('Waiting for messages...')
channel.start_consuming()



