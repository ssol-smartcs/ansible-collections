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
module: smartcs_tty_command
author: "Seiko Solutions Inc. (@naka-shin1)"
short_description: Send character string to device via ConsoleServer SmartCS
description:
- Send character string to device via ConsoleServer SmartCS
version_added: 1.3.0
extends_documentation_fragment:
- seiko.smartcs.smartcs
notes:
- Tested against SmartCS NS-2250 System Software Ver 2.1
options:
  cmd_timeout:
    description:
    - After sending the character string,set the timeout time to receive
      the response character string as a numerical value.
    default: 10
    type: int
  custom_response:
    description:
    - Returns values as the customized format to be able to recognize sent characters(execute_command)
      and received characters(response) easily.
    type: bool
    default: no
    version_added: "1.1.0"
  custom_response_delete_nl:
    description:
    - Deletes the line with only a line break in the custom_response output.
    type: bool
    default: no
    version_added: "1.1.0"
  custom_response_delete_lastline:
    description:
    - Deletes the last line of the custom_response output.
    type: bool
    default: no
    version_added: "1.1.0"
  error_detect_on_sendchar:
    description:
    - If an error occurs after sending the string set in sendchar, specify whether
      to send sendchar or not. When cancel is set, next sendchar won't be sent if
      an error occurs after sending the character string set in sendchar.
      If exec is set, sendchar will send the next sendchar even if sendchar's sending fails.
    default: cancel
    choices:
    - cancel
    - exec
    type: str
  error_detect_on_module:
    description:
    - When an error occurs after sending the character string set in sendchar, set whether
      the result of ansible-playbook command is "ok" or "failed".
      When ok is set, an error information isn't displayed and the result of ansible-playbook command is
      "ok" even if an error occurs after sending the character string set in sendchar.
      When failed is set, an error information is displayed and the result of ansible-playbook command is
      "failed" if an error occurs after sending the character string set in sendchar.
    default: ok
    choices:
    - failed
    - ok
    type: str
  error_recvchar_regex:
    description:
    - After sending the character string set in sendchar, set the list of strings to be
      detected as an error if the received string contains a specific string as a regular expression.
      It can be set up to 8 values in list format.
    type: list
    elements: str
  escape_cmd:
    description:
    - Specifies a string to be sent when the expected value is not received after the command
      specified in initial_prompt_check_cmd option is executed.
    version_added: "1.1.0"
    type: str
  escape_cmd_retry:
    description:
    - Specifies the number of retries for the escape_cmd.
    default: 3
    version_added: "1.1.0"
    type: int
  escape_cmd_timeout:
    description:
    - Specifies a timeout value for the escape_cmd.
    default: 5
    version_added: "1.1.0"
    type: int
  initial_prompt:
    description:
    - Specifies a string expected to be received after the command specified in
      initial_prompt_check_cmd option is executed.
    version_added: "1.1.0"
    type: str
  initial_prompt_check_cmd:
    description:
    - Specifies a string to be sent in the pre-check operation.
    default: '__NL__'
    version_added: "1.1.0"
    type: str
  initial_prompt_check_cmd_timeout:
    description:
    - Specifies a timeout value for the initial_prompt_check_cmd.
    default: 5
    version_added: "1.1.0"
    type: int
  nl:
    description:
    - Specify the line feed code to be sent.
    default: cr
    choices:
    - crlf
    - cr
    - lf
    type: str
  recvchar:
    description:
    - Set a list of received strings expected to be output after sending the string set in sendchar.
      It can be set up to 16 values in list format.
    type: list
    elements: str
  recvchar_regex:
    description:
    - Set a regular expression which has the same role as recvchar.
      It can be set up to 8 values in list format.
    type: list
    elements: str
  sendchar:
    description:
    - Set a list of strings to send to the target tty.
      This string will be sent in order from the top of the list.
    type: list
    elements: str
  src:
    description:
    - Specifies the file path that contains the strings to be sent to the target tty.
      The file path can be the absolute pathname or relative pathname from the playbook or
      role root directory.
      This option is exclusive with the sendchar option.
    type: str
    version_added: "1.1.0"
  tty:
    description:
    - Set the tty to send a string. It can be set in ttylist format (1-16, 1, 2-8, 16).
      An example
      1-5,21 --> 1,2,3,4,5,21
    required: true
    type: str
  ttycmd_debug:
    description:
    - A debug information is displayed after all strings set in sendchar have been sent.
    default: "off"
    choices:
    - "off"
    - "on"
    - "detail"
    type: str
"""

EXAMPLES = """
- name: Login to SmartCS and execute "show version"
  seiko.smartcs.smartcs_tty_command:
    tty: 1
    cmd_timeout : 5
    recvchar:
    - 'login: '
    - 'Password: '
    - 'SWITCH> '
    sendchar:
    - __NL__
    - user01
    - secret01
    - show version
"""

RETURN = """
stdout:
  description: The set of responses from the commands via SmartCS
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: ['...', '...']
stdout_lines:
  description: The value of stdout split into a list
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: [['...', '...'], ['...'], ['...']]
pre_stdout:
  description: The set of responses from the pre-check commands via SmartCS
  returned: When the initial_prompt setting is valid and the command is executed successfully
  type: list
  sample: ['...', '...']
pre_stdout_lines:
  description: The value of pre_stdout split into a list
  returned: When the initial_prompt setting is valid and the command is executed successfully
  type: list
  sample: [['...', '...'], ['...'], ['...']]
stdout_lines_custom:
  description: The custom value of responses from the commands via SmartCS
  returned: When the custom_response setting is valid and the command is executed successfully
  type: list
  sample: [{'execute_command':'...', 'response':['...', '...']}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    WAITSEC,
    NOWAIT,
    NOWAITSEC,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    terminal_ttymanage_waitstr_input,
    terminal_ttymanage_waitregex_input,
    terminal_ttymanage_errregex_input,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    check_cmdto,
    check_recvchar,
    check_return_error,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    get_clicmd_ttysend_waitset,
    get_clicmd_ttysend_delay,
    get_clicmd_ttysend,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    parse_cmd,
    parse_optsec,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    pre_check,
    pre_action,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    change_hyphen_list_to_comma_list,
    edit_responses,
    custom_responses,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    to_lines,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    run_commands,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    smartcs_argument_spec,
    check_args,
)


def param_to_commands(module):
    commands = list()

    tty = module.params['tty']
    nl = module.params['nl']
    cmd_timeout = module.params['cmd_timeout']
    error_detect_on_sendchar = module.params['error_detect_on_sendchar']
    recvchar = module.params['recvchar']
    recvchar_regex = module.params['recvchar_regex']
    error_recvchar_regex = module.params['error_recvchar_regex']
    sendchar = module.params['sendchar']
    src = module.params['src']

    if not tty:
        module.fail_json(msg='tty parameter is required')
    if not sendchar and not src:
        module.fail_json(msg='sendchar or src parameter is required')

    if src:
        sendchar = module.params['src'].splitlines()
    elif sendchar:
        sendchar = module.params['sendchar']

    # set nl
    commands.append('terminal ttymanage nl %s' % nl)

    # set cmd_timeout
    check_cmdto(module, cmd_timeout)
    commands.append('terminal ttymanage timeout %d' % cmd_timeout)

    # set error_detect_on_sendchar
    if error_detect_on_sendchar == 'cancel':
        commands.append('terminal ttymanage after_error cancel')
    else:
        commands.append('terminal ttymanage after_error execute')

    # <recvchar>
    #
    # set recvchar
    if recvchar:
        check_recvchar(module, recvchar, "recvchar", 16)
        for index, recv in enumerate(recvchar, 1):
            commands.append(terminal_ttymanage_waitstr_input(index, recv))

    # set recvchar_regex
    if recvchar_regex:
        check_recvchar(module, recvchar_regex, "recvchar_regex", 8)
        for index, recvr in enumerate(recvchar_regex, 1):
            commands.append(terminal_ttymanage_waitregex_input(index, recvr))

    # set error_recvchar_regex
    if error_recvchar_regex:
        check_recvchar(module, error_recvchar_regex, "error_recvchar_regex", 8)
        for index, erecv in enumerate(error_recvchar_regex, 1):
            commands.append(terminal_ttymanage_errregex_input(index, erecv))

    # <ttysend>
    #
    try:
        ttylist = change_hyphen_list_to_comma_list(tty)
    except ValueError:
        module.fail_json(msg='tty parameter is invalid. input value is an integer from 1 to 48')

    for ttynum in ttylist:
        # set tty
        commands.append('terminal ttymanage tty %d' % ttynum)
        for cmd in sendchar:
            cmd = str(cmd)

            # __WAIT__:sec
            if WAITSEC in cmd:
                cmd_l = parse_cmd(module, cmd, WAITSEC)
                timeout = parse_optsec(module, cmd, WAITSEC)
                commands.append(get_clicmd_ttysend_waitset(module, ttynum, nl, cmd_l, timeout))

            # __NOWAIT__:sec
            elif NOWAITSEC in cmd:
                cmd_l = parse_cmd(module, cmd, NOWAITSEC)
                delay = parse_optsec(module, cmd, NOWAITSEC)
                commands.append(get_clicmd_ttysend_delay(module, ttynum, nl, cmd_l, delay))

            # __NOWAIT__
            elif NOWAIT in cmd:
                cmd_l = parse_cmd(module, cmd, NOWAIT)
                commands.append(get_clicmd_ttysend(module, ttynum, nl, cmd_l))

            else:
                commands.append(get_clicmd_ttysend_waitset(module, ttynum, nl, cmd, cmd_timeout))

        if module.params['ttycmd_debug'] == 'off':
            pass
        elif module.params['ttycmd_debug'] == 'on':
            commands.append('show terminal ttymanage')
        elif module.params['ttycmd_debug'] == 'detail':
            commands.append('show terminal ttymanage detail')
        else:
            pass

    return commands


def main():
    """ Main entry point for Ansible module execution
    """
    argument_spec = dict(
        tty=dict(type='str', required=True),
        nl=dict(type='str', choices=['crlf', 'cr', 'lf'], default='cr'),
        cmd_timeout=dict(type='int', default=10),
        error_detect_on_sendchar=dict(type='str', choices=['cancel', 'exec'], default='cancel'),
        sendchar=dict(type='list', elements="str"),
        src=dict(type='str'),
        recvchar=dict(type='list', elements="str"),
        recvchar_regex=dict(type='list', elements="str"),
        error_recvchar_regex=dict(type='list', elements="str"),
        error_detect_on_module=dict(type='str', choices=['ok', 'failed'], default='ok'),
        custom_response=dict(type='bool', default=False),
        custom_response_delete_nl=dict(type='bool', default=False),
        custom_response_delete_lastline=dict(type='bool', default=False),
        initial_prompt=dict(type='str'),
        initial_prompt_check_cmd=dict(type='str', default='__NL__'),
        initial_prompt_check_cmd_timeout=dict(type='int', default=5),
        escape_cmd=dict(type='str'),
        escape_cmd_timeout=dict(type='int', default=5),
        escape_cmd_retry=dict(type='int', default=3),
        ttycmd_debug=dict(type='str', choices=['off', 'on', 'detail'], default='off')
    )

    argument_spec.update(smartcs_argument_spec)
    mutually_exclusive = [('sendchar', 'src')]
    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    result = {'changed': False}

    warnings = list()
    check_args(module, warnings)
    result['warnings'] = warnings

    if pre_check(module):
        pre_response = pre_action(module)

    commands = param_to_commands(module)
    result['commands'] = commands

    responses = run_commands(module, commands)

    responses = edit_responses(module, responses)
    check_return_error(module, responses)

    result.update({
        'changed': False,
        'stdout': responses,
        'stdout_lines': list(to_lines(responses))
    })

    cstm_resp = module.params['custom_response']
    if cstm_resp:
        result.update({
            'stdout_lines_custom': custom_responses(module, to_lines(responses),
                                                    module.params['custom_response_delete_nl'],
                                                    module.params['custom_response_delete_lastline'])
        })

    if pre_check(module):
        result.update({
            'pre_stdout': pre_response,
            'pre_stdout_lines': list(to_lines(pre_response))
        })

    module.exit_json(**result)


if __name__ == "__main__":
    main()
