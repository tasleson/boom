# Copyright (C) 2017 Red Hat, Inc., Bryn M. Reeves <bmr@redhat.com>
#
# grub2.py - Boom Grub2 integration
#
# This file is part of the boom project.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
"""The ``boom.grub2`` module defines functions for interacting with
    the Grub2 bootloader environment.
"""
from __future__ import print_function

from boom import *

from subprocess import Popen, PIPE

def grub2_get_env(name):
    """Return the value of the Grub2 environment variable with name
        ``name`` as a string.

        :param name: The name of the environment variable to return.
        :returns: The value of the named environment variable.
        :returntype: string
    """
    grub_cmd = ["grub2-editenv", "list"]
    try:
        p = Popen(grub_cmd, stdin=None, stdout=PIPE, stderr=PIPE)
        out = p.communicate()[0]
    except OSError as e:
        _log_error("Could not obtain grub2 environment: %s" % e)
        return ""

    for line in out.splitlines():
        (env_name, value) = line.split('=', 1)
        if name == env_name:
            return value
    return ""
        

# vim: set et ts=4 sw=4 :
