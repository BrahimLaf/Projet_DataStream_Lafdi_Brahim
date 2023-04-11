import pika
import hashlib
import re
import json
import geoip2.database
import requests
import urllib.request
from datetime import datetime, timezone, timedelta
from server import channel
from urllib.parse import urlparse
from models import CleanLog
from main import create_database, engine, Base
from sqlalchemy.orm import sessionmaker





# configuration des files d'attente et de l'échange
exchange_name = 'logs-exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
queue_name = 'queue-data-clean'
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='logs')

# Récupération de la session
Session = sessionmaker(bind=engine)
session = Session()

# Calcul du hash MD5 de la ligne de log
def get_log_id(log_line):
    hash_object = hashlib.md5(log_line.encode())
    log_id = hash_object.hexdigest()
    return log_id


def timestamp(line):
    timestamp_str = re.findall(r'\[(.*?)\]', line)[0]
    timestamp_obj = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
    # Ajouter le décalage horaire à l'heure UTC
    timestamp_obj -= timedelta(hours=timestamp_obj.utcoffset().total_seconds() // 3600)
    return timestamp_obj


# Fonction pour extraire le year, month, day_of_week, hourminuteseconde

def year_month_dayofweek_day_hourminuteseconde(timestamp_obj):
    year = timestamp_obj.year
    month = timestamp_obj.month
    day = timestamp_obj.day
    day_of_week = timestamp_obj.strftime('%A')
    hourminuteseconde = timestamp_obj.strftime('%H:%M:%S')
    return year, month, day, day_of_week,  hourminuteseconde


# Fonction pour extraire le fuseau horaire et le convertir en UTC+0
def convert_timezone(dt_str, tz_str):
    local_dt = datetime.strptime(dt_str, '%d/%b/%Y:%H:%M:%S %z')
    local_tz = timezone(timedelta(minutes=local_dt.utcoffset().total_seconds() // 60))
    target_tz = timezone(tz_str)
    target_dt = local_tz.normalize(local_dt.astimezone(target_tz))
    return target_dt.strftime('%Y-%m-%d %H:%M:%S')

# Fonction pour extraire adresse IP
def extract_ip(line):
    #ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
    ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
    if ip_match is None:
        raise ValueError("Impossible de trouver l'adresse IP dans la ligne de log")
    ip = ip_match.group(0)
    return ip

# Fonction pour extraire Pays et Ville
def get_geo_info(ip_address):
    url = f'http://ip-api.com/json/{ip_address}'
    try:
        response = requests.get(url)
        data = json.loads(response.content.decode('utf-8'))
        country = data['country']
        city = data['city']
        return country, city
    except Exception as e:
#        print(f"Erreur lors de l'extraction des informations de géolocalisation : {e}")
        return None, None

# Fonction pour extraire le user
def extract_user(line):
    user = re.search(r'\S+@\S+', line)
    if user is not None:
        return user.group(0)
    else:
        return line.split()[2]
    
# Fonction pour extraire Pl'email
def email(line):
    is_email = re.search(r'\S+@\S+', line)
    if is_email is not None:
        return "true"
    else:
        return "false"

# Fonction pour extraire Domaine
def email_domain(line):
    email = re.search(r'@\S+', line)
    if email is not None:
        domain = email.group(0)[1:]
        return domain.split()[0]
    else:
        return 'Pas de domain'   

# Fonction pour extraire Methode
def rest_method(line):
    # On utilise une expression régulière pour extraire la méthode HTTP
    # dans la ligne de log
    method = re.search(r'"(\S+)\s+\S+\s+\S+"', line)
    if method is not None:
        return method.group(1)
    else:
        return None

# Fonction pour extraire URL
def url(line):
    url_match = re.search(r'"(.*?)"', line)
    if url_match is not None:
        url = url_match.group(1).split()[1]
        return url
    else:
        return None
    
    
def schema_ext(line):
    url = line.split()[6]
    return urlparse(url).scheme


def host_ext(line):
    url = line.split()[6]
    return urlparse(url).hostname


  
def rest_version_ext(line):
    version = re.search(r'HTTP/\d\.\d', line)
    if version is not None:
        return version.group(0)
    else:
        return None    



def statut_ext(line):
    status = re.search(r'\s(\d{3})\s', line)
    if status is not None:
        return status.group(1)
    else:
        return None
    
    
# Fonction pour obtenir la signification d'un code de statut HTTP
def status_ext(line):
    status_code = re.search(r'" (\d+) ', line).group(1)
    if status_code == '200':
        return 'OK'
    elif status_code == '203':
        return 'Non-Authoritative Information'
    elif status_code == '206':
        return 'Partial Content'
    elif status_code == '226':
        return 'IM Used'
    elif status_code == '300':
        return 'Multiple Choices'		
    elif status_code == '404':
        return 'Not Found'
    elif status_code == '403':
        return 'Forbidden'
    elif status_code == '500':
        return 'Internal Server Error'
    else:
        return 'Other'


# Fonction pour convertir les bytes en kilo-octets et méga-octets


def size_bytes_ext(line):
    # Retirez les caractères '-' de la ligne
    line = line.replace('-', '')
    # Divisez la ligne en mots en utilisant l'espace comme séparateur
    words = line.split()
    # Le dernier mot de la ligne est la taille de la réponse en bytes
    size = int(words[-1])
    return size


def size_kilo_bytes_ext(line):
    size_in_kb = size_bytes_ext(line) / 1024
    return size_in_kb

def size_mega_bytes_ext(line):
    size_in_mb = size_bytes_ext(line) / (1024 * 1024)
    return size_in_mb
  
# Fonction pour prétraiter une ligne de log et stocker les données nettoyées dans la base de données
def clean_log(ch, method, properties, body):
#    try:
        line = body.decode('utf-8')
        id_match = re.search(r'\d{7}', line)
#        if id_match is None:
#            raise ValueError("Impossible de trouver l'ID dans la ligne de log")
#        id_tech = id_match.group(0)
        id = get_log_id(line)
        timestamp_obj = timestamp(line)
        year, month, day, day_of_week, hourminuteseconde = year_month_dayofweek_day_hourminuteseconde(timestamp_obj)
        ip = extract_ip(line)
        country, city = get_geo_info(ip)
        user = extract_user(line)
        is_email = email(line)
        Domaine = email_domain(line)
        Methode = rest_method(line)
        adress_url = url(line)
        schema = schema_ext(line)
        host = host_ext(line)
        rest_version = rest_version_ext(line)
        status = statut_ext(line)
        status_verbose = status_ext(line)
        size_bytes=  size_bytes_ext(line)
        size_kilo_bytes= size_kilo_bytes_ext(line)
        size_mega_bytes = size_mega_bytes_ext(line)     
         
        # Insertion de la ligne de log dans la base de données
        try:
            # Ajouter les données à la base de données
            clear_log = CleanLog(id=id, timestamp=timestamp_obj, year=year, month=month, day=day, day_of_week=day_of_week, hourminuteseconde=hourminuteseconde, 
                                ip=ip, country=country, city=city, user=user, is_email=is_email, Domaine= Domaine, Methode=Methode, url=adress_url, schema=schema,host=host, 
                                rest_version=rest_version, status=status, status_verbose=status_verbose, size_bytes=size_bytes, size_kilo_bytes=size_kilo_bytes,
                                size_mega_bytes=size_mega_bytes) 
            # Rechercher les doublons dans la base de données
            doublon = session.query(CleanLog).filter_by(id=id).one_or_none()
            if not doublon: 
                session.add(clear_log)
                session.commit()  # Valider la transaction
                print(f"Log inséré dans la base de données : {line}")
        except Exception as e:
            session.rollback()  # Annuler la transaction en cas d'erreur
            raise e
    
channel.basic_consume(queue=queue_name, on_message_callback=clean_log, auto_ack=True)
print("Attente de logs...")
channel.start_consuming()       
# Ecouter les logs
channel.basic_consume(queue=queue_name, on_message_callback=clean_log, auto_ack=True)


# Commencer à écouter les logs

print("Attente de logs...")
channel.start_consuming()

# fermeture de la session
session.close()