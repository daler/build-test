#!/bin/bash
set -e
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo bash Miniconda3-latest-Linux-x86_64.sh -b -p /anaconda
sudo chown -R $USER /anaconda
export PATH="/anaconda/bin:$PATH"
conda install -y conda-build
pip install docker-py
