# python 3.6

import random
import time
import os, platform, mysql.connector
import paho.mqtt.client as mqtt
import datetime
from datetime import datetime
import subprocess
from paho.mqtt import client as mqtt_client

conn = mysql.connector.connect(
        host='localhost',
        user='admin',
        password='',
        database='SAE31_db'
    )

broker = 'wewenito.ddns.net'
port = 1883
topic = "SAE301/PRISE1"
topic2 = "SAE301/PRISE2"
topic3 = "SAE301/PRISE3"

client_id = f'publish-{random.randint(0, 1000)}'

print(datetime.now())

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg, id, topicname):
    if topicname == 'PRISE1':
        result = client.publish(topic, msg)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nID = {id} : Envoyé `{msg}` sur le topic `{topic}`")
            
        else:
            print(f"Échec de l'envoi du message sur le topic {topic}, code de retour : {status}")
        time.sleep(1.5)

    elif topicname == 'PRISE2':
        result = client.publish(topic2, msg)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nID = {id} : Envoyé `{msg}` sur le topic `{topic2}`")
            
        else:
            print(f"Échec de l'envoi du message sur le topic {topic}, code de retour : {status}")
        time.sleep(1.5)

    elif topicname == 'PRISE3':
        result = client.publish(topic3, msg)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nID = {id} : Envoyé `{msg}` sur le topic `{topic3}`")
            
        else:
            print(f"Échec de l'envoi du message sur le topic {topic}, code de retour : {status}")
        time.sleep(1.5)


def publish_date(client, msg, id, topicname):
    if topicname == 'PRISE1':
        topic = f'SAE301/{topicname}/PLAGES1'
        result = client.publish(topic, msg)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nID = {id} : Envoyé les dates `{msg}` sur le topic `{topic}`")
          
            
        else:
            print(f"Échec de l'envoi du message sur le topic {topic}, code de retour : {status}")
        time.sleep(1.5)

    elif topicname == 'PRISE2':
        topic2 = f'SAE301/{topicname}/PLAGES1'
        result = client.publish(topic2, msg)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nID = {id} : Envoyé les dates `{msg}` sur le topic `{topic}`")
          
        else:
            print(f"Échec de l'envoi du message sur le topic {topic}, code de retour : {status}")
        time.sleep(1.5)

    elif topicname == 'PRISE3':
        topic3 = f'SAE301/{topicname}/PLAGES1'
        result = client.publish(topic3, msg)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nID = {id} : Envoyé les dates `{msg}` sur le topic `{topic}`")
          
            
        else:
            print(f"Échec de l'envoi du message sur le topic {topic}, code de retour : {status}")
        time.sleep(1.5)


def get_datetimedebut_1(x, id):
    while id<=x:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT datetime_debut FROM dubstep_app_plageshoraires where plages_on_off = 1 and id={id}")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
            return None

def get_datetimefin_1(x, id):
    while id<=x:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT datetime_fin FROM dubstep_app_plageshoraires where plages_on_off = 1 and id={id}")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
            return None

def get_datetimedebut_0(x, id):
    while id <= x:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT datetime_debut FROM dubstep_app_plageshoraires where plages_on_off = 0 and id={id}")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
            return None

def get_datetimefin_0(x, id):
    while id<=x:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT datetime_fin FROM dubstep_app_plageshoraires where plages_on_off = 0 and id={id}")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
            return None

def count():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM dubstep_app_plageshoraires ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("Aucune donnée trouvée dans la table.")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
        return None

def get_topicname(msg, id):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT topicname FROM dubstep_app_plageshoraires where plages_on_off = {msg} and id={id}")
        result = cursor.fetchone()
        if result:
            return result[0]
    except:
        print("gezzegzgzze")

def run():
    client = connect_mqtt()
    
    x = count()
    print(f'Nombre de lignes de la table : {x}')

    id=0
    y=0
    while y<x:
        y+=1
        id+=1
        latest_datetimedebut_1 = get_datetimedebut_1(x, id)
        latest_datetimefin_1 = get_datetimefin_1(x, id)

        latest_datetimedebut_0 = get_datetimedebut_0(x, id)
        latest_datetimefin_0 = get_datetimefin_0(x, id)
        
        try :

            if datetime.now() <= latest_datetimefin_1 and datetime.now() >= latest_datetimedebut_1:
                msg = "1"
                topicname = get_topicname(msg, id)
                publish(client, msg, id, topicname)
                msg = f'{latest_datetimedebut_1}/{latest_datetimefin_1}'
                publish_date(client, msg, id, topicname)

            
            else:
                print(f"\nLa plage horaire en ON n'est pas d'actualité pour l'ID {id}.\n")

            print(f"Plage horaire pour l'ID = {id}")
            print(f'Datetime exact : {datetime.now()}')
            print(f'Début on : {latest_datetimedebut_1}')
            print(f'Fin on :   {latest_datetimefin_1}')

        except Exception as e:
            print(f"\nAucune plage horaire correspondant à l'id {id} en ON.\n")


        try :

            if datetime.now() <= latest_datetimefin_0 and datetime.now() >= latest_datetimedebut_0:
               msg = "0"
               topicname = get_topicname(msg, id)
               publish(client, msg, id, topicname)
               msg = f'{latest_datetimedebut_0}/{latest_datetimefin_0}'
               publish_date(client, msg, id, topicname)

            else:
                print(f"La plage horaire en OFF n'est pas d'actualité pour l'ID {id}.")
            print(f"Plage horaire pour l'ID = {id}")
            print(f'Datetime exact : {datetime.now()}')
            print(f'Début off : {latest_datetimedebut_0}')
            print(f'Fin off :   {latest_datetimefin_0}\n')
            
        except:
            print(f"\nAucune plage horaire correspondant à l'id {id} en OFF.\n")


def run_loop(): #fonction pour faire une loop quand le programme tourne seul
    while True:
        run()
        print("\n-----------------------------------------------------------------\n")
        time.sleep(10) 


if __name__ == '__main__':
    run()
    #run_loop()






