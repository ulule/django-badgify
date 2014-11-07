#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get install -y python-software-properties
add-apt-repository ppa:fkrull/deadsnakes -y
apt-get update
apt-get install -y \
    build-essential \
    python-dev \
    python-setuptools \
    python-pip \
    python2.6-dev \
    python2.7-dev \
    python3.1-dev \
    python3.2-dev \
    python3.3-dev \
    python3.4-dev \
    libtiff4-dev \
    libjpeg8-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.5-dev \
    tk8.5-dev \
    python-tk \
    curl \
    git \
    gettext

pip install \
    virtualenv \
    autoenv

curl https://raw.githubusercontent.com/creationix/nvm/v0.17.3/install.sh | bash

echo "source /usr/local/bin/activate.sh" >> /home/vagrant/.bashrc
echo "source /home/vagrant/.nvm/nvm.sh" >> /home/vagrant/.bashrc

source /home/vagrant/.nvm/nvm.sh
nvm install 0.10
nvm use 0.10
nvm alias default 0.10

npm i -g bower
