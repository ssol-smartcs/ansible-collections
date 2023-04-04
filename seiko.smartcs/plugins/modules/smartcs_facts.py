#!/usr/bin/python
#
# Copyright (c) 2021 Seiko Solutions Inc. all rights reserved.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = """
module: smartcs_facts
author: "Seiko Solutions Inc. (@naka-shin1)"
short_description: Collect facts from SmartCS
description:
- Collects a base set of device facts from a SmartCS.
  This module prepends all of the
  base network fact keys with C(ansible_net_<fact>).  The facts
  module will always collect a base set of facts from the device
  and can enable or disable collection of additional facts.
version_added: 1.3.0
extends_documentation_fragment:
- seiko.smartcs.smartcs
notes:
- Tested against SmartCS NS-2250 System Software Ver 2.1
options:
  gather_subset:
    description:
    - When supplied, this argument restrict the facts collected to a given subset.
    - Possible values for this argument include C(all), C(config) and C(tty)
    - Specify a list of values to include a larger subset.
    - Use a values with an initial C(!) to collect all facts except that subset.
    required: false
    default: '!config'
    type: list
    elements: str
"""

EXAMPLES = """
- name: Collect all facts from the device
  seiko.smartcs.smartcs_facts:
    gather_subset: all

- name: Collect only the config and default facts
  seiko.smartcs.smartcs_facts:
    gather_subset:
    - config

- name: Do not collect tty facts
  seiko.smartcs.smartcs_facts:
    gather_subset:
    - "!tty"
"""

RETURN = """
ansible_net_gather_subset:
  description: The list of fact subsets collected from the device
  returned: always
  type: list

# default
ansible_net_model:
  description: The model name returned from the device
  returned: always
  type: str
ansible_net_serialnum:
  description: The serial number of the remote device
  returned: always
  type: str
ansible_net_version:
  description: The operating system version running on the remote device
  returned: always
  type: str
ansible_net_mainsystem:
  description: The operating system version of main system of the remote device
  returned: always
  type: str
ansible_net_backupsystem:
  description: The operating system version of backup system of the remote device
  returned: always
  type: str
ansible_net_bootconfig:
  description: The boot config of the remote device
  returned: always
  type: str
ansible_net_bootrom:
  description: The BootROM version running on the remote device
  returned: always
  type: str
ansible_net_hostname:
  description: The configured hostname of the device
  returned: always
  type: str
ansible_net_bond1:
  description: The configured bond1 interfaces of the remote device
  returned: always
  type: dict
ansible_net_eth1:
  description: The configured eth1 interfaces of the remote device
  returned: always
  type: dict
ansible_net_eth2:
  description: The configured eth1 interfaces of the remote device
  returned: always
  type: dict

# tty
ansible_net_tty:
  description:
    - The configured each tty information
    - baud, bitchar, flow, parity, stop, and label
  returned: when tty is configured
  type: list

# config
ansible_net_config:
  description: The current active config from the device
  returned: when config is configured
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.argspec.facts.facts import (
    FactsArgs,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.facts.facts import (
    Facts,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    smartcs_argument_spec,
)


def main():
    """
    Main entry point for module execution

    :returns: ansible_facts
    """
    argument_spec = FactsArgs.argument_spec
    argument_spec.update(smartcs_argument_spec)
    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True
    )
    warnings = []
    result = Facts(module).get_facts()

    ansible_facts, additional_warnings = result
    del ansible_facts["ansible_network_resources"]

    warnings.extend(additional_warnings)
    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()
