#!/bin/bash

# Function to install dependencies
install_dependencies() {
    # Install pip if not already installed
    pip install --upgrade pip

    # Install virtualenv if not already installed
    pip install virtualenv

    # Create a virtual environment
    python3 -m venv venv

    # Activate the virtual environment
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt
}

# Check for Heroku environment
if [ "$DYNO" ]; then
    install_dependencies
    python videobot.py

# Check for Replit environment
elif [ "$REPL_ID" ]; then
    install_dependencies
    python videobot.py

# Local environment
else
    sudo apt-get update

    install_dependencies
    python videobot.py
fi
