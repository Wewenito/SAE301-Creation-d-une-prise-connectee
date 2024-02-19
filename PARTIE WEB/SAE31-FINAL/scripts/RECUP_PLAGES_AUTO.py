import paho.mqtt.client as mqtt
import datetime
from datetime import datetime
import os, platform, mysql.connector
import sys

def clear_terminal():
    # Clear terminal screen based on the operating system
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def connect_brocker(client, userdata, flags, rc):
    client.subscribe("SAE301/PRISE1/PLAGES1")
    client.subscribe("SAE301/PRISE2/PLAGES1")
    client.subscribe("SAE301/PRISE3/PLAGES1")
    client.subscribe("SAE301/PRISE1/PLAGES2")
    client.subscribe("SAE301/PRISE2/PLAGES2")
    client.subscribe("SAE301/PRISE3/PLAGES2")


#+===========================================================================================================+
#|                                ENREGISTREMENT DES DONNEES DANS LA BDD                                     |
#+===========================================================================================================+



def insert_data_to_db(datetime_debut, datetime_fin, on_off, topicname):

    conn = mysql.connector.connect(
    host='localhost',
    user='admin',
    password='',
    database='SAE31_db'
)
    cursor = conn.cursor()

    query = "INSERT INTO dubstep_app_plageshoraires (datetime_debut, datetime_fin, plages_on_off, topicname) VALUES (%s, %s, %s, %s)"
    data = (datetime_debut, datetime_fin, on_off, topicname)
    

    try:
        cursor.execute(query, data)
        conn.commit()
        print(query)


    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:  # 1062 is le code d'erreur MySQL pour une entrée en double
            print(f"Doublon détecté : {data}")
        else:
            print(f"Erreur d'insertion : {error}")
    
    except Exception as error:
        print(f"Erreur inattendue : {error}")
    
    finally:
        cursor.close()  # Fermer le curseur
        conn.close()     # Fermer la connexion à la base de données

#+===========================================================================================================+
#|                              RECUPERATION, TRI & AFFICHAGE DES DONNEES                                    |
#+===========================================================================================================+

def get_data(client, userdata, msg):

    #clear_terminal()
    topicname = str(msg.topic)
    topicname = topicname.split('/')
    topicname = topicname[1]

    message_complet = msg.payload.decode() #Message non trié
    split = message_complet.split('/')

    datetime_debut = split[0]
    datetime_fin = split[1]

    on_off = 1

    try :
        insert_data_to_db(datetime_debut, datetime_fin, on_off, topicname)
        print(f'Le message {message_complet} est envoyé avec succès.\n')

    except Exception as error:
        print(f'Erreur de connexion avec mysql : {error}')





client = mqtt.Client()
client.on_connect = connect_brocker
client.on_message = get_data

client.connect("wewenito.ddns.net", 1883, 60)
#client.connect("test.mosquitto.org", 1883, 60)

client.loop_forever()
