#!/bin/bash

# Maximum installation check for extreme cases (e.g. someone who insalled Desktop Environment on a previously headless server).
sudo apt install macchanger python3 python3-pip python3-tk python3-venv -y

if python3 -c "import customtkinter" &> /dev/null; then
    echo "-----------------------------------------------"
    echo "customtkinter is already installed. Skipping..."
    echo "-----------------------------------------------"
else
    echo "-------------------------------------------------------------------"
    echo "customtkinter not found. Attempting a standard install with venv..."
    echo "-------------------------------------------------------------------"

# Adding a virtul environment so that it don't have to use "--break-system-packages".
python3 -m venv ss_venv

# Activating the virtual environment.
source ss_venv/bin/activate

# Installing the requirements.
if python3 -m pip install customtkinter; then
        echo "--------------------------------------------"
        echo "Successfully installed customtkinter safely."
        echo "--------------------------------------------"
    else
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "Standard installation failed due to OS restrictions (PEP 668)."
        echo "To fix this, we can use the --break-system-packages flag."
        echo "This might conflict with other system Python tools."
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

        read -p "Do you want to force the installation? (y/n): " confirm
        
        if [[ $confirm == [Yy]* ]]; then
            echo "Proceeding with system-wide installation..."
            python3 -m pip install customtkinter --break-system-packages
        else
            echo "Installation aborted by user."
            echo "Please manually troubleshoot or DM me on 'linkedin.com/in/kaucher-islam-forhad' for assistence."
            exit 1
        fi
    fi
fi

echo "-------------------------"
echo "Setup complete. Run with:" 
echo "python3 ShadowSwitch.py"
echo "-----------------------"

# Giving ShadowSwitch exicutable permissions, just in case.
chmod +x ShadowSwitch.py
