#!/bin/bash
set -e
if [[ $TRAVIS_OS_NAME == "linux" ]]; then tag="Linux-x86_64"; else tag="MacOSX-x86_64"; fi
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-${tag}.sh
sudo bash Miniconda3-latest-${tag}.sh -b -p /anaconda
sudo chown -R $USER /anaconda
mkdir -p /anaconda/conda-bld/osx-64 # workaround for bug in current conda
mkdir -p /anaconda/conda-bld/linux-64 # workaround for bug in current conda
export PATH="/anaconda/bin:$PATH"

if [[ $TRAVIS_OS_NAME == "linux" ]]; then
    pip install docker-py
fi

conda install -y anaconda-client
conda config --add channels https://conda.anaconda.org/t/$ANACONDA_TOKEN/daler
