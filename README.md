# Projet d'analyse des logs en temps réel avec Python, RabbitMQ et MySQL

Objectif

L'objectif de ce projet est de créer un système d'analyse des logs d'un serveur web en temps réel en utilisant Python, RabbitMQ et MySQL. Le système comprend un producteur (logs-producer) qui lit ligne par ligne un fichier de logs web-server-nginx.log, les publie dans un échange de type topic, et les envoie à deux files d'attente différentes : queue-data-lake et queue-data-clean. Le système comprend également deux consommateurs, data-lake-consumer et data-clean-consumer, qui traitent chaque file d'attente différemment en temps réel.
Dossier assets

Ce dossier contient le fichier web-server-nginx.log qui sera utilisé comme source de logs pour le projet.
Fichier .env

Ce fichier contient les informations de configuration sous forme de variables d'environnement pour le projet. Les valeurs des variables sont les suivantes :

makefile

RABBIT_USER=Brahim
RABBIT_PASSWORD=Badr064
user = 'root'
password = ''
host = 'localhost'
port = '3308'
database = 'DataStream'

Ces valeurs seront utilisées pour se connecter au serveur RabbitMQ et à la base de données MySQL dans le projet.
Fichier config.py

Ce fichier contient la configuration pour charger les variables d'environnement à partir du fichier .env. Il utilise la bibliothèque dotenv pour charger les variables d'environnement dans le projet. Les variables d'environnement sont stockées dans un dictionnaire nommé CONFIG qui peut être utilisé pour accéder aux valeurs de configuration dans d'autres parties du projet.
Fichier server.py

Ce fichier contient le code pour établir une connexion avec le serveur RabbitMQ en utilisant les informations de configuration du fichier .env. Il utilise la bibliothèque pika pour interagir avec RabbitMQ. Une fois la connexion établie, un objet de canal est créé pour envoyer et recevoir des messages à partir du serveur RabbitMQ.
Fichier docker-compose.yml

Ce fichier contient la configuration pour les services Docker nécessaires dans le projet. Il configure trois services : RabbitMQ, MySQL et PhpMyAdmin. RabbitMQ est utilisé comme broker de messages pour la communication entre les différents composants du projet. MySQL est utilisé comme base de données pour stocker les données traitées à partir des logs. PhpMyAdmin est utilisé comme interface web pour gérer la base de données MySQL.
Fichier logs-producer.py

Ce fichier contient le code pour lire le fichier de logs web-server-nginx.log à partir du dossier assets et publier chaque ligne de log dans un échange RabbitMQ. Les logs sont publiés avec une clé de routage 'logs' dans deux files d'attente différentes : 'queue-data-lake' et 'queue-data-clean'. Ces files d'attente seront utilisées par d'autres composants du projet pour consommer et traiter les logs.
Fichier main.py

Ce fichier contient le code principal du projet. Il est responsable de la création de la base de données MySQL si elle n'existe pas déjà, de la création d'une chaîne de connexion à la base de données en utilisant les informations de configuration du fichier .env, et de la définition du modèle de table RawLog en utilisant la bibliothèque SQLAlchemy. Il crée également une instance de session pour interagir avec la base de

données MySQL.
Fichier data-lake-consumer.py

Ce fichier contient le code du consommateur data-lake-consumer, qui est responsable de consommer les logs à partir de la file d'attente 'queue-data-lake' et de les traiter en temps réel. Il utilise la bibliothèque pika pour se connecter au serveur RabbitMQ, créer une file d'attente, et consommer les messages de la file d'attente. Les logs sont ensuite traités selon les besoins du projet, par exemple, ils peuvent être stockés dans la base de données MySQL, ou analysés pour obtenir des statistiques ou des informations spécifiques.
Fichier data-clean-consumer.py

Ce fichier contient le code du consommateur data-clean-consumer, qui est responsable de consommer les logs à partir de la file d'attente 'queue-data-clean' et de les traiter en temps réel. Le traitement des logs dans ce consommateur peut inclure le nettoyage des données, l'extraction d'informations spécifiques, ou l'envoi des données à d'autres systèmes pour traitement ultérieur. Le consommateur utilise également la bibliothèque pika pour se connecter au serveur RabbitMQ et consommer les messages de la file d'attente.
Conclusion

En résumé, ce projet met en œuvre un système d'analyse des logs d'un serveur web en temps réel en utilisant Python, RabbitMQ et MySQL. Il comprend un producteur pour lire les logs à partir d'un fichier, les publier dans un échange RabbitMQ, et les envoyer à deux files d'attente différentes. Il comprend également deux consommateurs pour traiter les logs en temps réel à partir des files d'attente. Les logs peuvent être stockés dans une base de données MySQL, analysés pour obtenir des statistiques ou des informations spécifiques, ou nettoyés avant d'être utilisés dans d'autres systèmes.
