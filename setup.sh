#!/bin/bash

sudo apt install macchanger -y
sudo apt install python3 -y

python3 -m venv ShadowSwitch
source ShadowSwitch/bin/activate
pip3 install -r requirements.txt
