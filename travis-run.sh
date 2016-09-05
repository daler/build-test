#!/bin/bash
export PATH=/anaconda/bin:$PATH

RECIPE=recipes/argh

if [[ $TRAVIS_OS_NAME = "linux" ]]
then
    python conda_build_with_docker.py $RECIPE --host-conda-bld /anaconda/conda-bld
else
    conda build $RECIPE
fi

anaconda -t $ANACONDA_TOKEN upload -u $CONDA_USER $(conda build --output $RECIPE)
