import paho.mqtt.client as mqtt
import datetime
from datetime import datetime
import os, platform, mysql.connector
import math

def clear_terminal():
    # Clear terminal screen based on the operating system
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def connect_brocker(client, userdata, flags, rc):
    client.subscribe("SAE301/PRISE1/PRESSION")
    client.subscribe("SAE301/PRISE2/PRESSION")
    client.subscribe("SAE301/PRISE3/PRESSION")


#+===========================================================================================================+
#|                                ENREGISTREMENT DES DONNEES DANS LA BDD                                     |
#+===========================================================================================================+

def insert_data_to_db(pression, date, topicname, altitude):
    conn = mysql.connector.connect(
        host='localhost',
        user='gab',
        password='',
        database='SAE31_db'
    )

    cursor = conn.cursor()

    date = str(datetime.now())

    
    query = "INSERT INTO dubstep_app_pression (pression, date, topicname, altitude) VALUES (%s, %s, %s, %s)"
    data = (pression, date, topicname, altitude)

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

    pression = float(msg.payload.decode())

    L = 0.0065  # Temperature lapse rate (K/m)
    R = 8.31432  # Universal gas constant (N·m/mol·K)
    M = 0.0289644  # Molar mass of Earth's air (kg/mol)
    g0 = 9.80665  # Standard acceleration due to gravity (m/s^2)
    T0 = 288.15  # Standard temperature at sea level (K)
    P0 = 1013.25 #Standard sea pressure

    #calcul hauteur du ciel
    h = (R * T0) / (M * g0)

    #calcul altitude
    altitude = h * math.log(P0 / pression)

    date = str(datetime.now())

    try :
        insert_data_to_db(message_complet, date, topicname, altitude)
        print(f'La pression actuelle {message_complet}Hpa a été envoyé avec succès.')
        print(f"L'altitude {altitude}m a été calculée avec succès.\n")

    except Exception as error:
        print(f'Erreur get data : {error}')





client = mqtt.Client()
client.on_connect = connect_brocker
client.on_message = get_data

client.connect("wewenito.ddns.net", 1883, 60)
#client.connect("test.mosquitto.org", 1883, 60)

client.loop_forever()
