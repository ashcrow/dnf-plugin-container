# Copyright (C) 2017 Steve Milner
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""
Update containers like you update packages.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

from argparse import Namespace

import dnf.cli

from Atomic import backendutils, syscontainers, util

from dnfpluginscore import _, logger


@dnf.plugin.register_command
class ContainerCommand(dnf.cli.Command):
    """
    A command which works with updating local containers.
    """

    aliases = ('container',)
    summary = _('Checks installed containers for update')

    @staticmethod
    def set_argparser(parser):
        parser.add_argument(
            'subcommand', nargs=1, choices=['check', 'update'])

    def configure(self):
        """
        Atomic libs require root.
        """
        self.cli.demands.root_user = True
        self.be_utils = backendutils.BackendUtils()
        self.debug = self.base.conf.debuglevel > 5

    def run(self):
        """
        Execute the Container command.
        """
        subcommand = self.opts.subcommand[0]

        # Check if updates are available
        if subcommand == 'check':
            self._check()
        # Update containers
        elif subcommand == 'update':
            self._update()

    def _check(self):
        """
        Check installed containers and note if updates are availabe.
        """
        container_list = self.be_utils.get_containers()
        needs_update = []

        # If there is at least one container ....
        if len(container_list) > 0:
            logger.info("Checking %s local container(s) for updates",
                        len(container_list))
            # For each container we have ....
            for container in container_list:
                logger.debug("Checking: {} {} {} {}".format(
                    container.name, container.original_structure.get('Type'),
                    container.created, container.image_name))
                inspection = util.skopeo_inspect(
                    'docker://' + container.image_name)
                digest = inspection.get('Digest', ':').split(':')[1]
                # Match the local image digest with the remote digest
                if digest != container.image:
                    needs_update.append((container, digest))
                logger.debug(
                    '%s: local=%s remote=%s',
                    container.name, container.image, digest)

            # Let the operator know of each container that could be updates
            if needs_update:
                logger.info('The following containers need updating:')
                for container, digest in needs_update:
                    logger.info('\t%s', container.name)
                logger.info('')
                logger.info(
                    'To update your containers use dnf containers '
                    'update or, to update specific containers, the '
                    'atomic command')
                logger.info('Example: sudo atomic containers update %s',
                            needs_update[0][0].name)
            else:
                logger.info("No updates found")
        else:
            logger.debug("No containers found")
        return needs_update

    def _update(self):
        """
        Update installed containers.
        """
        needs_update = self._check()
        if len(needs_update) > 0:
            if self.base.conf.assumeyes or (
                not self.base.conf.assumeno and self.base.output.userconfirm(
                    msg='Update? [y/N]: ', defaultyes_msg='Update? [Y/n]: ')):
                    for container, digest in needs_update:
                        self._pull_existing_tag(container)
                        self._update_container(container)

    def _update_container(self, container):
        """
        Update a container to the latest image.
        """
        logger.info('Updating %s ...', container.name)
        sc = syscontainers.SystemContainers()
        sc.args = Namespace(remote=True)
        try:
            if sc.get_checkout(container.name):
                return sc.update_container(
                    container.name, [], container.image_name)
            else:
                raise dnf.exceptions.Error(
                    'Could not find checkout for {}'.format(container.name))
        except ValueError as err:
            raise dnf.exceptions.Error(err)

    def _pull_existing_tag(self, container):
        """
        Update the container to the latest version for the tag.
        """
        try:
            be, img_obj = self.be_utils.get_backend_and_image_obj(
                container.image_name,
                str_preferred_backend=container.backend.backend,
                required=True)
            input_name = img_obj.input_name
        except ValueError:
            raise dnf.exceptions.Error(
                "{} not found locally.  Unable to update".format(
                    container.name))

        force = True
        # ostree doesn't allow force
        if container.backend.backend == 'ostree':
            force = False

        logger.info('Pulling %s ...', input_name)
        be.update(
            input_name, debug=self.debug, force=force, image_object=img_obj)

    # Currently not used
    '''
    def _latest_image(self, image):
        """
        Returns an image using the latest tag.
        """
        return image.rsplit(':', 1)[0] + ":latest"

    def _pull_latest(self, container):
        """
        Pull latest image.
        """
        if not container.backend.available():
            raise dnf.exceptions.Error(
                'Backend {} not available'.format(container.backend.backend))

        # Modified from Atomic/pull.py
        try:
            if container.backend.backend == 'docker':
                remote_image_obj = container.backend.make_remote_image(
                    self.args.image)
                if remote_image_obj.is_system_type:
                    container.backend = self.be_utils.get_backend_from_string(
                        'ostree')
                    self.be_utils.message_backend_change('docker', 'ostree')

            elif container.backend.backend == "containers-storage":
                remote_image_obj = container.backend.make_remote_image(
                    container.image_name)
            else:
                remote_image_obj = None

            latest = self._latest_image(container.image_name)
            logger.info('Pulling %s ...', latest)
            # Execute the image pull
            container.backend.pull_image(
                latest, remote_image_obj, debug=self.debug,
                assumeyes=self.base.conf.assumeyes)
        except ValueError as e:
            raise ValueError("Failed: {}".format(e))
    '''
