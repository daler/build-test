#!/bin/bash

# ensure we can install it
conda install -y --channel file:///anaconda/conda-bld --override-channels argh

# delete it from the channel (since this is a test repo after all...)
anaconda -t $ANACONDA_TOKEN remove -f $CONDA_USER/argh/0.26.1
