#!/bin/bash

python /home/frigiel/Documents/VSCODE/Django/SAE31/scripts/RECUP_ALL.py &

python /home/frigiel/Documents/VSCODE/Django/SAE31/scripts/RECUP_TEMP.py &

python /home/frigiel/Documents/VSCODE/Django/SAE31/scripts/RECUP_PRESSION.py &

python /home/frigiel/Documents/VSCODE/Django/SAE31/scripts/RECUP_HUMIDITE.py &

python /home/frigiel/Documents/VSCODE/Django/SAE31/scripts/RECUP_PLAGES_AUTO.py &

python /home/frigiel/Documents/VSCODE/Django/SAE31/scripts/main.py &

wait
