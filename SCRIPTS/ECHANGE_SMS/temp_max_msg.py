import paho.mqtt.client as mqtt
import subprocess, time

connected = False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("SAE301/PRISE1/TEMP")

def on_disconnect(client, userdata, flags, rc):
    print("brocker connection lost")



def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection. Trying to reconnect...")
        while True:
            try:
                client.reconnect()
                print("Reconnected to MQTT broker")
                break
            except Exception as e:
                print(f"Reconnection failed: {str(e)}. Retrying in 5 seconds...")
                time.sleep(5)

# Define the on_message function to call send_sms with the received message
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    send_sms(message)


def send_sms(message):
    try:
        message = float(message)
    except:
        print("The message received could not be converted into a float, discarding it..\n\n")


    if message > 50:
        print(f"The current temperature : {message} is above safe range, sending an alert")

        parameter = message

        #try:
        subprocess.call(['sh', 'envoi_mess.sh', str(parameter)])
        #except:
        #    print("The message could not be sent.. a new try will be done in a few seconds..")
    else:
        print(f"Current temperature is : {message}")
        print("The temperature is in the acceptable range")

    #print("Received message: " + message)


# Initialize the MQTT client
client = mqtt.Client()
client.on_connect = on_connect


client.on_message = on_message

client.on_disconnect = on_disconnect


print("connecting to the brocker..\n")
# Connect to the MQTT broker
while connected == False:
    try:

        client.connect("wewenito.ddns.net", 1883, 60)
        connected = True
    except:
        connected = False
        print("Connection failed, trying again in 5 seconds..")
        time.sleep(5)


client.loop_forever()
