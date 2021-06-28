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
module: smartcs_config
author: "Seiko Solutions Inc. (@naka-shin1)"
short_description: Manage configuratin sections of SmartCS
description:
- This module provides configuration of SmartCS.
  If there is a difference between running configration and a command specfied by the
  lines option, execute configration command.
version_added: 1.3.0
extends_documentation_fragment:
- seiko.smartcs.smartcs
notes:
- Tested against SmartCS NS-2250 System Software Ver 2.1
options:
  lines:
    description:
    - The ordered set of commands that should be configured in the
      section. The commands must be the exact same commands as found
      in the device running-config.
    type: list
    elements: str
    aliases:
    - commands
  src:
    description:
    - Specifies the source path to the file that contains the configuration
      to load.  The path to the source file can
      either be the full path on the Ansible control host or a relative
      path from the playbook or role root directory.
    type: str
  match:
    description:
    - Instructs the module on the way to perform the matching of
      the set of commands against the current device config.  If
      match is set to I(line), commands are matched line by line.
      if match is set to I(none), the module will not attempt to compare
      the source configuration with the running configuration on the remote device.
    choices:
    - line
    - none
    type: str
    default: line
  backup:
    description:
    - This argument will cause the module to create a full backup of the current C(running-config)
      from the remote device before any changes are made. If the C(backup_options)
      value is not given, the backup file is written to the C(backup) folder in the
      playbook root directory or role root directory, if playbook is part of an ansible
      role. If the directory does not exist, it is created.
    type: bool
    default: no
  save_when:
    description:
    - When changes are made to the device running-configuration, the
      changes are not copied to non-volatile storage by default.  Using
      this argument will change that before.  If the argument is set to
      I(always), then the running-configratoin will always be copied to the
      startup-configration and the I(modified) flag will always be set to
      True.  If the argument is set to I(modified), then the running-configration
      will only be copied to the startup-configration if it has changed since
      the last save to startup-configration.  If the argument is set to
      I(never), the running-configration will never be copied to the
      startup-configration.  If the argument is set to I(changed),
      then the running-configration will only be copied to the startup-configration
      if the task has made a change.
    default: never
    choices:
    - always
    - never
    - modified
    - changed
    type: str
"""

EXAMPLES = """
- name: configuration tty 1 settings
  seiko.smartcs.smartcs_config:
    lines:
    - pord tty 1 label SWITCH_1
    - set tty 1 baud 38400

- name: configuration tty 20 settings and write
  seiko.smartcs.smartcs_config:
    lines:
    - set pord tty 20 label ROUTER
    - set tty 20 baud 19200
    save_when: modified

- name: configuration host name and get backup file
  seiko.smartcs.smartcs_config:
    lines:
    - set hostname SmartCS_TEST1
    save_when: always
    backup: yes
"""

RETURN = """
updates:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['set hostname NS-2250-48', 'set tty 1 baud 19200']
commands:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['set hostname NS-2250-48', 'set tty 1 baud 19200']
backup_path:
  description: The full path to the backup file
  returned: when backup is yes
  type: str
  sample: /playbooks/ansible/backup/smartcs_config.2019-03-16@16:00:16
"""

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    run_commands,
    get_config,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    get_connection,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    smartcs_argument_spec,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    compareble_config,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)


def check_args(module, warnings):
    pass


def edit_config(connection, commands, module):
    try:
        connection.edit_config(candidate=commands)
    except Exception:
        module.fail_json(msg='An invalid command was specified. \"%s\"' % commands)


def get_candidate_config(module):
    candidate = ''
    if module.params['src']:
        candidate = module.params['src']

    elif module.params['lines']:
        candidate_obj = NetworkConfig(indent=1)
        candidate_obj.add(module.params['lines'], parents=None)
        candidate = dumps(candidate_obj, 'raw')

    return candidate


def get_running_config(module, current_config=None, flags=None):
    running = get_config(module, flags=flags)

    return running


def save_config(module, result):
    result['changed'] = True
    if not module.check_mode:
        write_command = [{
            'command': 'write',
            'prompt': r' \[y\/n\] ? ',
            'answer': 'y\r',
            'newline': False
        }]
        run_commands(module, write_command)
    else:
        module.warn('Skipping command `write` due to check_mode.')


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        src=dict(type='str'),
        lines=dict(aliases=['commands'], type='list', elements="str"),
        match=dict(default='line', choices=['line', 'none']),
        backup=dict(type='bool', default=False),
        save_when=dict(
            choices=['always', 'never', 'modified', 'changed'], default='never'
        )
    )

    argument_spec.update(smartcs_argument_spec)

    mutually_exclusive = [('lines', 'src')]

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    result = {'changed': False}

    warnings = list()
    check_args(module, warnings)
    result['warnings'] = warnings

    contents = None
    flags = []
    connection = get_connection(module)

    if module.params['backup']:
        contents = get_config(module, flags=flags)
        if module.params['backup']:
            result['__backup__'] = contents

    if any((module.params['lines'], module.params['src'])):
        match = module.params['match']

        candidate = get_candidate_config(module)
        running = get_running_config(module, contents, flags=flags)
        try:
            response = connection.get_diff(candidate=candidate, running=running, diff_match=match,
                                           diff_ignore_lines=None, path=None, diff_replace=None)
        except ConnectionError as exc:
            module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))

        config_diff = response['config_diff']

        if config_diff:
            commands = config_diff.split('\n')

            result['commands'] = commands
            result['updates'] = commands

            # send the configuration commands to the device and merge
            # them with the current running config
            if not module.check_mode:
                edit_config(connection, commands, module)

            result['changed'] = True

    startup_config = None

    if module.params['save_when'] == 'always':
        save_config(module, result)
    elif module.params['save_when'] == 'modified':
        output = run_commands(module, ['show config running', 'show config startup'])

        running_config = NetworkConfig(indent=1, contents=output[0], ignore_lines=None)
        startup_config = NetworkConfig(indent=1, contents=output[1], ignore_lines=None)

        running_config_compareble, startup_config_compareble = compareble_config(running_config, startup_config)

        if running_config_compareble != startup_config_compareble:
            save_config(module, result)
    elif module.params['save_when'] == 'changed' and result['changed']:
        save_config(module, result)

    if module._diff:
        output = run_commands(module, 'show config running')
        contents = output[0]

    module.exit_json(**result)


if __name__ == '__main__':
    main()
