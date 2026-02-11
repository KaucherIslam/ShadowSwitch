#!/bin/bash

# 1. Install system requirements
sudo apt update && sudo apt install macchanger python3 python3-pip python3-tk python3-venv -y

# 2. Display Choice
echo "--------------------------------------------------------------"
echo "Standard installation failed due to OS restrictions (PEP 668)."
echo "Force install is ~99% safe as 'customtkinter' doesn't conflict"
echo "with core OS tools. Otherwise, use an isolated folder (venv). "
echo "--------------------------------------------------------------"

read -p "Do you want to force the installation? (y/n): " confirm
        
if [[ $confirm == [Yy]* ]]; then
    echo "Proceeding with system-wide installation..."
    python3 -m pip install customtkinter --break-system-packages
else
    echo "Setting up isolated virtual environment..."
    python3 -m venv ss_venv
    # Use the direct path to pip to guarantee it installs inside ss_venv
    ./ss_venv/bin/pip install customtkinter
fi

# 3. Finalize Permissions
echo "--------------------------------------------------"
echo "Initial setup complete. If you chose 'y' run with:" 
echo "python3 ShadowSwitch.py                           "
echo "                                                  "
echo "Or everyone can run with:                         "
echo "bash start.sh                                     "
echo "Or                                                "
echo "./start.sh                                        "
echo "--------------------------------------------------"

chmod +x ShadowSwitch.py
chmod +x start.sh
