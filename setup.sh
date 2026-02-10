#!/bin/bash

# For installing macchanger & python if incase the user dosen't have it.
sudo apt install macchanger python3 -y

# Adding a virtul environment so that it don't have to use "--break-system-packages".
python3 -m venv ss_venv

# Activating the virtual environment.
source ss_venv/bin/activate

# Installing the requirements.
pip3 install -r requirements.txt

# Giving ShadowSwitch exicutable permissions, just in case.
chmod +x ShadowSwitch.py
