import paho.mqtt.client as mqtt
import datetime
from datetime import datetime
import os, platform, mysql.connector

def clear_terminal():
    # Clear terminal screen based on the operating system
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def connect_brocker(client, userdata, flags, rc):
    client.subscribe("SAE301/PRISE1/TEMP")
    client.subscribe("SAE301/PRISE2/TEMP")
    client.subscribe("SAE301/PRISE3/TEMP")


#+===========================================================================================================+
#|                                ENREGISTREMENT DES DONNEES DANS LA BDD                                     |
#+===========================================================================================================+

def insert_data_to_db(temp, date, topicname):
    conn = mysql.connector.connect(
        host='localhost',
        user='gab',
        password='',
        database='SAE31_db'
    )

    cursor = conn.cursor()

    date = str(datetime.now())

    
    query = "INSERT INTO dubstep_app_temp (temp, date, topicname) VALUES (%s, %s, %s)"
    data = (temp, date, topicname)

    print(query)
    
    try:
        cursor.execute(query, data)
        conn.commit()
        conn.close()

    except Exception as error:
        print(error)

#+===========================================================================================================+
#|                              RECUPERATION, TRI & AFFICHAGE DES DONNEES                                    |
#+===========================================================================================================+

def get_data(client, userdata, msg):

    #clear_terminal()
    topicname = str(msg.topic)
    topicname = topicname[7:]

    message_complet = msg.payload.decode() #Message non trié

    date = str(datetime.now())

    try :
        insert_data_to_db(message_complet, date, topicname)
        print(f'Le message {message_complet} est envoyé avec succès.\n')

    except Exception as error:
        print(f'Erreur get data : {error}')





client = mqtt.Client()
client.on_connect = connect_brocker
client.on_message = get_data

client.connect("wewenito.ddns.net", 1883, 60)
#client.connect("test.mosquitto.org", 1883, 60)

client.loop_forever()
