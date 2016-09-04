Test repo for working out how to build conda recipes via a docker container.

This supports cases where conda and conda-build are not even installed on the
host (though `--host-conda-bld` will have to be specified so that packages have
somewhere to be built).

If `conda-bld` is available on the host, packages are built in the host's
conda-bld directory with the proper permissions. This way, packages can be
built in a uniform environment independent of the host environment, and the
packages can be installed and tested locally before uploading to a channel.

Arbitrary docker containers can be used, as long as they have conda-build
installed; for now the default is `condaforge/linux-anvil`.

Getting permissions to work correctly is [trickier than it
sounds](https://github.com/docker/docker/issues/2259). Here, the solution is to
build a custom docker image that matches the uid:gid of the user running the
module, and runs conda-build as that user inside the docker container. Since
all that is added to the base image is a `useradd` and `groupadd` command, the
build process is very fast.
