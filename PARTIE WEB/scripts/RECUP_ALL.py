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
    client.subscribe("SAE301/PRISE1")
    client.subscribe("SAE301/PRISE2")
    client.subscribe("SAE301/PRISE3")


#+===========================================================================================================+
#|                                ENREGISTREMENT DES DONNEES DANS LA BDD                                     |
#+===========================================================================================================+

conn = mysql.connector.connect(
    host='localhost',
    user='gab',
    password='',
    database='SAE31_db'
)

def insert_data_to_db(date, on_off, topicname):

    print(1)
    cursor = conn.cursor()
    print(2)

    date = str(datetime.now())
    print(3)

    query = "INSERT INTO dubstep_app_donnees (date, on_off, topicname) VALUES (%s, %s, %s)"
    print(4)
    data = (date, on_off, topicname)
    print(5)
    

    try:
        cursor.execute(query, data)
        conn.commit()
        print(query)


    except Exception as error:
        print(f"Erreur d'insertion : {error}")

#+===========================================================================================================+
#|                              RECUPERATION, TRI & AFFICHAGE DES DONNEES                                    |
#+===========================================================================================================+

def get_data(client, userdata, msg):

    #clear_terminal()
    topicname = str(msg.topic)
    topicname = topicname[7:]

    message_complet = msg.payload.decode() #Message non trié

    if message_complet == '1' or message_complet == '0':
        date = str(datetime.now())
        try :
            insert_data_to_db(date, message_complet, topicname)
            print(f'Le message {message_complet} est envoyé avec succès.\n')
        except Exception as error:
            print(f'Erreur de connexion avec mysql : {error}')

    elif message_complet == 'H':
        x = 0
        while x < 10:
            x+=1
            print('MEGA HOT MEGA HOT MEGA HOT MEGA HOT MEGA HOT MEGA HOT')

    else :
        print(f"Erreur : le message {message_complet} est incorrect, seuls 0 et 1 sont acceptés.\n")




client = mqtt.Client()
client.on_connect = connect_brocker
client.on_message = get_data

client.connect("wewenito.ddns.net", 1883, 60)
#client.connect("test.mosquitto.org", 1883, 60)

client.loop_start()
