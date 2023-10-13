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
module: smartcs_command
author: "Seiko Solutions Inc. (@naka-shin1)"
short_description: Run commands on remote devices running SmartCS
description:
- Sends arbitrary commands to an SmartCS node and returns the results
  read from the device. This module includes an
  argument that will cause the module to wait for a specific condition
  before returning or timing out if the condition is not met.
  This module does not support running commands in configuration mode.
  Please use M(seiko.smartcs.smartcs_config) to configure SmartCS.
version_added: 1.3.0
extends_documentation_fragment:
- seiko.smartcs.smartcs
notes:
- Tested against SmartCS NS-2250 System Software Ver 2.1
options:
  commands:
    description:
    - List of commands to send to the remote smartcs over the
      configured provider. The resulting output from the command
      is returned. If the I(wait_for) argument is provided, the
      module is not returned until the condition is satisfied or
      the number of retries has expired. If a command sent to the
      device requires answering a prompt, it is possible to pass
      a dict containing I(command), I(answer) and I(prompt).
      Common answers are 'y' or "\\r" (carriage return, must be
      double quotes). See examples.
    required: true
    type: list
    elements: raw
  wait_for:
    description:
    - List of conditions to evaluate against the output of the
      command. The task will wait for each condition to be true
      before moving forward. If the conditional is not true
      within the configured number of retries, the task fails.
      See examples.
    aliases:
    - waitfor
    type: list
    elements: str
  match:
    description:
    - The I(match) argument is used in conjunction with the
      I(wait_for) argument to specify the match policy.  Valid
      values are C(all) or C(any).  If the value is set to C(all)
      then all conditionals in the wait_for must be satisfied.  If
      the value is set to C(any) then only one of the values must be
      satisfied.
    default: all
    type: str
    choices:
    - any
    - all
  retries:
    description:
    - Specifies the number of retries a command should by tried
      before it is considered failed. The command is run on the
      target device every retry and evaluated against the
      I(wait_for) conditions.
    default: 10
    type: int
  interval:
    description:
    - Configures the interval in seconds to wait between retries
      of the command. If the command does not pass the specified
      conditions, the interval indicates how long to wait before
      trying the command again.
    default: 1
    type: int
"""

EXAMPLES = """
- name: run show version on remote devices
  seiko.smartcs.smartcs_command:
    commands: show version

- name: run show version and check to see if output contains NS-2250
  seiko.smartcs.smartcs_command:
    commands: show version
    wait_for: result[0] contains NS-2250

- name: run multiple commands on remote nodes
  seiko.smartcs.smartcs_command:
    commands:
    - show version
    - show ipinterface

- name: run multiple commands and evaluate the output
  seiko.smartcs.smartcs_command:
    commands:
    - show version
    - show ipinterfaces
    wait_for:
    - result[0] contains NS-2250
    - result[1] contains lo

- name: run commands that require answering a prompt
  seiko.smartcs.smartcs_command:
    commands:
    - command: 'copy startup 2 to startup 4'
      prompt: 'Do you really want to copy external startup1 to external startup3 [y/n] ? '
      answer: 'y'
    - command: 'clear startup 2'
      prompt: 'Do you really want to clear external & internal startup2 [y/n] ? '
      answer: "y"
"""

RETURN = """
stdout:
  description: The set of responses from the commands
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: ['...', '...']
stdout_lines:
  description: The value of stdout split into a list
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: [['...', '...'], ['...'], ['...']]
failed_conditions:
  description: The list of conditionals that have failed
  returned: failed
  type: list
  sample: ['...', '...']
"""
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import (
    Conditional,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    ComplexList,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    run_commands,
    to_lines,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    smartcs_argument_spec,
    check_args,
)


def parse_commands(module, warnings):
    command = ComplexList(dict(
        command=dict(key=True),
        prompt=dict(),
        answer=dict()
    ), module)
    commands = command(module.params['commands'])
    items = []

    for item in commands:
        if module.check_mode and not item['command'].startswith('show'):
            warnings.append('only show commands are supported when using '
                            'check mode, not executing `%s`' % item['command'])
        else:
            items.append(item)
    return items


def main():
    """main entry point for module execution
    """
    argument_spec = dict(
        commands=dict(type='list', elements="raw", required=True),
        wait_for=dict(type='list', elements="str", aliases=['waitfor']),
        match=dict(default='all', choices=['all', 'any']),
        retries=dict(default=10, type='int'),
        interval=dict(default=1, type='int')
    )

    argument_spec.update(smartcs_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    result = {'changed': False}

    warnings = list()
    check_args(module, warnings)
    commands = parse_commands(module, warnings)
    result['warnings'] = warnings

    wait_for = module.params['wait_for'] or list()
    conditionals = [Conditional(c) for c in wait_for]

    retries = module.params['retries']
    interval = module.params['interval']
    match = module.params['match']

    while retries > 0:
        responses = run_commands(module, commands)

        for item in list(conditionals):
            if item(responses):
                if match == 'any':
                    conditionals = list()
                    break
                conditionals.remove(item)

        if not conditionals:
            break

        time.sleep(interval)
        retries -= 1

    if conditionals:
        failed_conditions = [item.raw for item in conditionals]
        msg = 'One or more conditional statements have not been satisfied'
        module.fail_json(msg=msg, failed_conditions=failed_conditions)

    result.update({
        'changed': False,
        'stdout': responses,
        'stdout_lines': list(to_lines(responses))
    })

    module.exit_json(**result)


if __name__ == '__main__':
    main()
