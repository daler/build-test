#!/bin/bash

if [[ $TRAVIS_OS_NAME = "linux" ]]; then tag="Linux-x86_64"; else tag="MacOSX-x_86_64"; fi
# install conda
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-${tag}.sh
sudo bash Miniconda3-latest-${tag}.sh -b -p /anaconda
sudo chown -R $USER /anaconda
mkdir -p /anaconda/conda-bld/osx-64 # workaround for bug in current conda
mkdir -p /anaconda/conda-bld/linux-64 # workaround for bug in current conda
export PATH=/anaconda/bin:$PATH
conda install -y --file requirements.txt
conda index /anaconda/conda-bld/linux-64 /anaconda/conda-bld/osx-64

# setup bioconda channel
# conda config --add channels bioconda
# conda config --add channels r
conda config --add channels file://anaconda/conda-bld

# setup bioconda-utils
#pip install git+https://github.com/bioconda/bioconda-utils.git
