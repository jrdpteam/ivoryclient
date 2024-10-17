#!/bin/bash

echo "Updating the system..."
sudo apt update

echo "Installing PyQt5 and PySocks dependencies..."
pip3 install pyqt5 pysocks

echo "Checking and installing Tor..."
sudo apt install tor -y
sudo systemctl disable tor
sudo systemctl restart tor

echo "Installation complete. You can now run your client!"
