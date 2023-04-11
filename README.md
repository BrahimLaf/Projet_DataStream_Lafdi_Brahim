# Projet d'analyse des logs en temps réel avec Python, RabbitMQ et MySQL


<h2> Objectif : </h2>

L'objectif de ce projet est de créer un système d'analyse des logs d'un serveur web en temps réel en utilisant Python, RabbitMQ et MySQL. Le système comprend un producteur (logs-producer) qui lit ligne par ligne un fichier de logs web-server-nginx.log, les publie dans un échange de type topic, et les envoie à deux files d'attente différentes : queue-data-lake et queue-data-clean. Le système comprend également deux consommateurs, data-lake-consumer et data-clean-consumer, qui traitent chaque file d'attente différemment en temps réel.

<h2> Architechture : </h2>

![image](https://user-images.githubusercontent.com/115103788/231180603-0db8c6c0-f124-4dae-98ee-7090916e9b6a.png)


## Structure du projet

Le projet contient les fichiers suivants :

- `assets/web-server-nginx.log`: Un fichier de logs de serveur web nginx utilisé comme source de données pour l'application.
- `.env`: Un fichier de configuration contenant les informations de connexion à RabbitMQ et à MySQL.
- `config.py`: Un fichier de configuration Python qui charge les variables d'environnement à partir du fichier `.env`.
- `server.py`: Un fichier Python qui établit une connexion avec RabbitMQ en utilisant les informations de configuration du fichier `config.py`.
- `docker-compose.yml`: Un fichier de configuration Docker Compose qui définit les services RabbitMQ, MySQL et phpMyAdmin nécessaires pour l'exécution de l'application.
- `logs-producer.py`: Un fichier Python qui lit le fichier de logs `assets/web-server-nginx.log` et publie chaque ligne dans les files d'attente RabbitMQ.
- `main.py`: Le fichier principal de l'application qui traite les logs à partir des files d'attente RabbitMQ, les nettoie et les stocke dans une base de données MySQL.
- `models.py`: Un fichier Python qui définit les modèles de table utilisés par l'application.
- `data-clean-consumer`: responsable de consommer les logs à partir de la file d'attente 'queue-data-clean' et de les traiter en temps réel, en nettoyant les données, en extrayant des informations spécifiques, ou en les envoyant à d'autres systèmes pour traitement ultérieur.
- `data-lake-consumer` : responsable de consommer les logs à partir de la file d'attente 'queue-data-lake' et de les traiter en temps réel, par exemple en les stockant dans une base de données MySQL, en les analysant pour obtenir des statistiques ou des informations spécifiques.

## Prérequis

Avant d'exécuter l'application, vous devez vous assurer d'avoir les éléments suivants installés :

- Python 3.x
- Docker
- Docker Compose

<h2>1.	Environnement virtuel</h2>

J’ai travaillé dans un environnement virtuel qui est un mécanisme qui permet de séparer les dépendances requises par différents projets en créant des environnements virtuels qui sont isolés entre eux.</p>


## Configuration

Avant d'exécuter l'application, vous devez configurer les variables d'environnement dans le fichier `.env`. Voici les variables à configurer :

### Fichier .env
      RABBIT_USER=Brahim
      RABBIT_PASSWORD=Badr064
      user=root
      password=
      host=localhost
      port=3308
      database=DataStream

Ces valeurs seront utilisées pour se connecter au serveur RabbitMQ et à la base de données MySQL dans le projet.

###  Fichier docker-compose.yml
Ce fichier contient la configuration pour les services Docker nécessaires dans le projet. Il configure trois services : RabbitMQ, MySQL et PhpMyAdmin. RabbitMQ est utilisé comme broker de messages pour la communication entre les différents composants du projet. MySQL est utilisé comme base de données pour stocker les données traitées à partir des logs. PhpMyAdmin est utilisé comme interface web pour gérer la base de données MySQL.
![image](https://user-images.githubusercontent.com/115103788/231185438-506eb103-1146-4721-9106-4c7af29e38bc.png)



### Dossier assets : 
Ce dossier contient le fichier web-server-nginx.log qui sera utilisé comme source de logs pour le projet.

![image](https://user-images.githubusercontent.com/115103788/231184989-a8dcf413-de95-41ed-8854-758c58b75344.png)


###  Fichier config.py

Ce fichier contient la configuration pour charger les variables d'environnement à partir du fichier .env. Il utilise la bibliothèque dotenv pour charger les variables d'environnement dans le projet. Les variables d'environnement sont stockées dans un dictionnaire nommé CONFIG qui peut être utilisé pour accéder aux valeurs de configuration dans d'autres parties du projet.

![image](https://user-images.githubusercontent.com/115103788/231185170-cada97ab-bb54-4faa-87cb-9cd954036b9f.png)


###  Fichier server.py

Ce fichier contient le code pour établir une connexion avec le serveur RabbitMQ en utilisant les informations de configuration du fichier .env. Il utilise la bibliothèque pika pour interagir avec RabbitMQ. Une fois la connexion établie, un objet de canal est créé pour envoyer et recevoir des messages à partir du serveur RabbitMQ.

![image](https://user-images.githubusercontent.com/115103788/231185569-2fff5128-e77d-473c-b248-071b21ceb3a0.png)

###  Fichier main.py

Ce fichier contient le code principal du projet. Il est responsable de la création de la base de données MySQL si elle n'existe pas déjà, de la création d'une chaîne de connexion à la base de données en utilisant les informations de configuration du fichier .env, et de la définition du modèle de table RawLog en utilisant la bibliothèque SQLAlchemy. Il crée également une instance de session pour interagir avec la base de données MySQL.

![image](https://user-images.githubusercontent.com/115103788/231185880-8d8035cb-cd81-4d57-919d-12087487e211.png)

###  Fichier models.py

Ce fichier contient la définition du modèle de table CleanLog en utilisant la bibliothèque SQLAlchemy. La classe CleanLog est définie avec les colonnes et les types de données correspondants pour stocker les informations de logs traitées. Ce modèle sera utilisé pour mapper les logs traités à partir du fichier de logs aux enregistrements dans la base de données MySQL.

![image](https://user-images.githubusercontent.com/115103788/231186388-429ade20-5486-4d94-a1b8-48da755239a4.png)


###  Fichier logs-producer.py

Ce fichier contient le code pour lire le fichier de logs web-server-nginx.log à partir du dossier assets et publier chaque ligne de log dans un échange RabbitMQ. Les logs sont publiés avec une clé de routage 'logs' dans deux files d'attente différentes : 'queue-data-lake' et 'queue-data-clean'. Ces files d'attente seront utilisées par d'autres composants du projet pour consommer et traiter les logs.

![image](https://user-images.githubusercontent.com/115103788/231186619-bb84150d-4b6b-43d4-9dd1-8ff352640b35.png)


###  Fichier data-lake-consumer.py

Ce fichier contient le code du consommateur data-lake-consumer, qui est responsable de consommer les logs à partir de la file d'attente 'queue-data-lake' et de les traiter en temps réel. Il utilise la bibliothèque pika pour se connecter au serveur RabbitMQ, créer une file d'attente, et consommer les messages de la file d'attente. Les logs sont ensuite traités selon les besoins du projet, par exemple, ils peuvent être stockés dans la base de données MySQL, ou analysés pour obtenir des statistiques ou des informations spécifiques.

![image](https://user-images.githubusercontent.com/115103788/231186711-3d614ead-d5f8-4413-ae87-a60384e086d9.png)

###  Fichier data-clean-consumer.py

Ce fichier contient le code du consommateur data-clean-consumer, qui est responsable de consommer les logs à partir de la file d'attente 'queue-data-clean' et de les traiter en temps réel. Le traitement des logs dans ce consommateur peut inclure le nettoyage des données, l'extraction d'informations spécifiques, ou l'envoi des données à d'autres systèmes pour traitement ultérieur. Le consommateur utilise également la bibliothèque pika pour se connecter au serveur RabbitMQ et consommer les messages de la file d'attente.

![image](https://user-images.githubusercontent.com/115103788/231186776-f0fab344-2c06-449e-b8f6-7fbba89b4438.png)



###  Conclusion

En résumé, ce projet met en œuvre un système d'analyse des logs d'un serveur web en temps réel en utilisant Python, RabbitMQ et MySQL. Il comprend un producteur pour lire les logs à partir d'un fichier, les publier dans un échange RabbitMQ, et les envoyer à deux files d'attente différentes. Il comprend également deux consommateurs pour traiter les logs en temps réel à partir des files d'attente. Les logs peuvent être stockés dans une base de données MySQL, analysés pour obtenir des statistiques ou des informations spécifiques, ou nettoyés avant d'être utilisés dans d'autres systèmes.
