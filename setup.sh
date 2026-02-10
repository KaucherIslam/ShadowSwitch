#!/bin/bash

sudo apt install macchanger -y
sudo apt install python3 -y

python3 -m venv ss_venv
source ss_venv/bin/activate
pip3 install -r requirements.txt
