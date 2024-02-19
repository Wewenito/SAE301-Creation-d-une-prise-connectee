#!/bin/bash

python3 /home/lizzie/SAE31/scripts/RECUP_ALL.py &

python3 /home/lizzie/SAE31/scripts/RECUP_TEMP.py &

python3 /home/lizzie/SAE31/scripts/RECUP_PRESSION.py &

python3 /home/lizzie/SAE31/scripts/RECUP_HUMIDITE.py &

python3 /home/lizzie/SAE31/scripts/RECUP_PLAGES_AUTO.py &

python3 /home/lizzie/SAE31/scripts/main.py &

wait
