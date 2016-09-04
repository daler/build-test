#!/usr/bin/env python

"""
To ensure conda packages are built in the most compatible manner, we can use
a docker container. This module supports using a docker container to build
conda packages in the local channel which can later be uploaded to anaconda.

Building local packages in a docker container is trickier than it sounds due to
permission handling. Docker runs as root, so any files it makes are owned by
root. We can use the `-u` flag when running docker to make it run as that user.
But that user in turn must exist in the docker container itself. One solution
would be to require this script to be run as a particular UID. Another would be
to wrap everything done by docker with a `sudo chown` to set permissions
correctly.

Instead, here we build a new docker image whose user uid and
gid match that of the user running this module. Since this is a simple useradd
command and it uses cached images, this is very fast. Then we can rely on the
container running as the correct uid and gid and making files appear on the
filesystem with the correct permissions.
"""

import os
import subprocess as sp
from pprint import pprint
import pwd
import grp
import argparse
from io import BytesIO
from docker import Client as DockerClient


class RecipeBuilder(object):
    """
    Builds a conda recipe in the conda-bld directory using a docker container.
    """
    def __init__(
        self, tag, base_url='unix://var/run/docker.sock',
        container_recipe='/tmp',
        container_conda_bld='/home/{username}/conda-bld',
        image='condaforge/linux-anvil',
    ):
        """
        Builds a container based on `image`, adding the local user and group to
        the container.
        tag:
            Tag to use for the built container
        """
        self.tag = tag
        self.image = image
        uid = os.getuid()
        usr = pwd.getpwuid(uid)
        self.user_info = dict(
            uid=uid,
            gid=usr.pw_gid,
            groupname=grp.getgrgid(usr.pw_gid).gr_name,
            username=usr.pw_name)
        self.container_recipe = container_recipe
        self.container_conda_bld = container_conda_bld.format(**self.user_info)
        self.docker = DockerClient(base_url=base_url)
        self._build = None

    def _build_container(self):
        """
        Builds a new container based on the provided image that has the current
        user and groups added to the image and ensures the conda-bld directory is
        present.
        """
        dockerfile = """
        FROM {self.image}
        RUN groupadd -g {gid} {groupname} && useradd -u {uid} -g {gid} {username}
        RUN mkdir -p {self.container_conda_bld}
        """.format(self=self, **self.user_info)
        f = BytesIO(dockerfile.encode('utf-8'))
        response = self.docker.build(fileobj=f, rm=True, tag=self.tag)
        self._build = ''.join(i.decode() for i in response)
        return self._build

    def host_conda_build_dir(self, recipe):
        """
        Identifies the conda-bld directory on the host
        """
        return os.path.dirname(
            os.path.dirname(
                sp.check_output(
                    ['conda', 'build', recipe, '--output'],
                    universal_newlines=True
                ).splitlines()[0]
            )
        )

    def run_docker_cmd(self, cmd, binds=None):
        """
        Run a command in the docker container `tag`
        """
        if not self._build:
            self._build_container()
        container = self.docker.create_container(
            image=self.tag,
            user=self.user_info['uid'],
            command=cmd,
            host_config=self.docker.create_host_config(binds=binds, network_mode='host'))
        cid = container['Id']
        self.docker.start(container=cid)
        status = self.docker.wait(container=cid)
        stdout = self.docker.logs(container=cid, stdout=True, stderr=False).decode()
        stderr = self.docker.logs(container=cid, stderr=True, stdout=False).decode()
        return dict(status=status, stdout=stdout, stderr=stderr)

    def build_recipe(self, recipe):
        recipe = os.path.abspath(recipe)
        binds = {
            recipe: {
                'bind': '/tmp',
                'mode': 'ro'
            },
            self.host_conda_build_dir(recipe): {
                'bind': self.container_conda_bld,
                'mode': 'rw'
            },
        }
        pprint(binds)
        res = self.run_docker_cmd(
            'conda build {0}'.format(self.container_recipe),
            binds=binds,
        )
        if res['status'] != 0:
            print(res['stderr'])
            print(res['stdout'])

if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=RecipeBuilder.__doc__)
    ap.add_argument('recipe', help='Recipe directory to build')
    ap.add_argument('--image', default='condaforge/linux-anvil',
                    help='Docker image to build with. Expected to have '
                    'at least conda-build installed')
    ap.add_argument('--container-conda-bld', default='/home/{username}/conda-bld',
                    help='The conda-bld directory in the container. Can use '
                    'placeholders "username", "groupname", "uid", "gid"')
    ap.add_argument('--tag', default='ttt', help='Tag for the built docker container')
    ap.add_argument('--container-recipe', default='/tmp',
                    help='Mounts the provided recipe in this directory in the container')
    ap.add_argument('--base_url', default='unix://var/run/docker.sock')
    args = ap.parse_args()
    builder = RecipeBuilder(
        tag=args.tag,
        container_recipe=args.container_recipe,
        container_conda_bld=args.container_conda_bld,
        image=args.image,
        base_url=args.base_url
    )
    builder.build_recipe(args.recipe)
