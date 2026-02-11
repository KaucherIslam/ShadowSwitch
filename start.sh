#!/bin/bash

# Check if the user chose 'Y/y' or else:
if [ -d "ss_venv" ]; then
    # Activate the Virtual Environment
    source ss_venv/bin/activate
fi

# Launch the tool
python3 ShadowSwitch.py
