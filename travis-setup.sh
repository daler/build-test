#!/bin/bash
set -e
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo bash Miniconda3-latest-Linux-x86_64.sh -b -p /anaconda
sudo chown -R $USER /anaconda
mkdir -p /anaconda/conda-bld/osx-64 # workaround for bug in current conda
mkdir -p /anaconda/conda-bld/linux-64 # workaround for bug in current conda
export PATH="/anaconda/bin:$PATH"
pip install docker-py
