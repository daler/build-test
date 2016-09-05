#!/bin/bash
export PATH=/anaconda/bin:$PATH
if [[ $TRAVIS_OS_NAME = "linux" ]]
then
    python conda_build_with_docker.py recipes/argh --host-conda-bld /anaconda/conda-bld
else
    conda build recipes/argh
fi
