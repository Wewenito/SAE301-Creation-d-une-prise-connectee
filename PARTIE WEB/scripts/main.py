import subprocess
import time

while True:
    # Exécute le programme PUBLISH_MQTT.py en tant que sous-processus
    process = subprocess.Popen(['python', '/home/frigiel/Documents/VSCODE/Django/SAE31/scripts/PUBLISH_MQTT_PLAGES.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(10)

    # Kill le sous-processus
    process.terminate()

    # Attendez que le sous-processus se termine complètement
    process.wait()

    print("\nRestarting PUBLISH_MQTT.py...\n")
