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
pip3 install urllib3
pip3 install beautifulsoup4
pip3 install telepota
pip3 install captcha
pip3 install googletrans==3.1.0a0
pip3 install Google-Images-Search
pip3 install google-cloud-speech
pip3 install google-cloud-pubsub
pip3 install google-cloud-scheduler
pip3 install google-cloud-vision
pip3 install ShazamAPI
pip3 install opencv-python
pip3 install forex-python
pip3 install price-parser
pip3 install ChatterBot-corpus
pip3 install awscli==1.11.18
pip3 install SQLAlchemy==1.3.6
pip3 install Mako==1.1.2
pip3 install levenshtein
pip3 install ChatterBot==1.0.4
pip3 install pytz
pip3 install spacy
python3 -m spacy download en