#!/bin/sh
#
# This script will install all the dependencies for the project.
# This script is made for Ubuntu 22.04 LTS x86_64
#
# Usage:
# ./DependencyInstaller.sh
#
# -----------------------------------------------------------------------------
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.11
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2
sudo update-alternatives --config python3
sudo apt-get install -y git-all
sudo apt-get install -y python3-pip
sudo apt-get install -y libfreetype6-dev
sudo apt-get install -y screen
sudo apt install -y ffmpeg
sudo apt-get install git-lfs
git-lfs install
pip3 install --upgrade pip
pip3 install -r requirements.txt
git clone https://github.com/MekhyW/telepota.git
cd telepota
python3 setup.py install