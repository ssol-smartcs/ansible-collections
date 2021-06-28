# Copyright (c) 2021 Seiko Solutions Inc. all rights reserved.
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2016 Red Hat Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re
import os

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list, ComplexList,
)
from ansible.module_utils.connection import Connection, ConnectionError
from ansible.module_utils.six import string_types
from ansible.module_utils.six.moves.urllib.parse import urlsplit

_DEVICE_CONFIGS = {}

smartcs_provider_spec = {
    'host': dict(),
    'port': dict(type='int'),
    'username': dict(fallback=(env_fallback, ['ANSIBLE_NET_USERNAME'])),
    'password': dict(
        fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']), no_log=True
    ),
    'ssh_keyfile': dict(
        fallback=(env_fallback, ['ANSIBLE_NET_SSH_KEYFILE']), type='path'
    ),
    'authorize': dict(
        default=False,
        fallback=(env_fallback, ['ANSIBLE_NET_AUTHORIZE']),
        type='bool'
    ),
    'auth_pass': dict(
        fallback=(env_fallback, ['ANSIBLE_NET_AUTH_PASS']), no_log=True
    ),
    'timeout': dict(type='int')
}
smartcs_argument_spec = {
    'provider': dict(
        type='dict',
        options=smartcs_provider_spec,
    )
}


def get_provider_argspec():
    return smartcs_provider_spec


def get_connection(module):
    if hasattr(module, '_smartcs_connection'):
        return module._smartcs_connection

    capabilities = get_capabilities(module)
    network_api = capabilities.get('network_api')
    if network_api == 'cliconf':
        module._smartcs_connection = Connection(module._socket_path)
    else:
        module.fail_json(msg='Invalid connection type %s' % network_api)

    return module._smartcs_connection


def get_capabilities(module):
    if hasattr(module, '_smartcs_capabilities'):
        return module._smartcs_capabilities
    try:
        capabilities = Connection(module._socket_path).get_capabilities()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
    module._smartcs_capabilities = json.loads(capabilities)
    return module._smartcs_capabilities


def check_args(module, warnings):
    pass


def get_defaults_flag(module):
    connection = get_connection(module)
    try:
        out = connection.get_defaults_flag()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
    return to_text(out, errors='surrogate_then_replace').strip()


def get_config(module, flags=None):
    flags = to_list(flags)
    flag_str = ' '.join(to_list(flags))

    try:
        return _DEVICE_CONFIGS[flag_str]
    except KeyError:
        connection = get_connection(module)
        try:
            out = connection.get_config(flags=flags)
        except ConnectionError as exc:
            module.fail_json(
                msg=to_text(exc, errors='surrogate_then_replace')
            )
        cfg = to_text(out, errors='surrogate_then_replace').strip()
        _DEVICE_CONFIGS[flag_str] = cfg
        return cfg


def to_commands(module, commands):
    spec = {
        'command': dict(key=True),
        'prompt': dict(),
        'answer': dict()
    }
    transform = ComplexList(spec, module)
    return transform(commands)


def run_commands(module, commands, check_rc=True):
    connection = get_connection(module)
    try:
        return connection.run_commands(commands=commands, check_rc=check_rc)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))


def load_config(module, commands):
    connection = get_connection(module)

    try:
        resp = connection.edit_config(commands)
        return resp.get('response')
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))


def to_lines(stdout):
    for item in stdout:
        try:
            if isinstance(item, string_types):
                item = str(item).split('\n')
            yield item
        except UnicodeEncodeError:
            if isinstance(item, string_types):
                item = to_text(item).split("\n")
            yield item


def _get_working_path(self):
    cwd = self._loader.get_basedir()
    if self._task._role is not None:
        cwd = self._task._role._role_path
    return cwd


def handle_template(self):
    src = self._task.args.get('src')
    working_path = self._get_working_path()
    if os.path.isabs(src) or urlsplit('src').scheme:
        source = src
    else:
        source = self._loader.path_dwim_relative(working_path, 'templates', src)
        if not source:
            source = self._loader.path_dwim_relative(working_path, src)
    if not os.path.exists(source):
        raise ValueError('path specified in src not found')
    try:
        with open(source, 'r') as f:
            template_data = to_text(f.read())
    except IOError:
        return dict(failed=True, msg='unable to load src file')
    # Create a template search path in the following order:
    # [working_path, self_role_path, dependent_role_paths, dirname(source)]
    searchpath = [working_path]
    if self._task._role is not None:
        searchpath.append(self._task._role._role_path)
        if hasattr(self._task, "_block:"):
            dep_chain = self._task._block.get_dep_chain()
            if dep_chain is not None:
                for role in dep_chain:
                    searchpath.append(role._role_path)
    searchpath.append(os.path.dirname(source))
    self._templar.environment.loader.searchpath = searchpath
    self._task.args['src'] = self._templar.template(template_data)


def flatten(array):
    res = []
    for el in array:
        if isinstance(el, (list, tuple)):
            res.extend(flatten(el))
            continue
        res.append(el)
    return res


def compareble_config(running_config, startup_config):
    running_config_compareble = re.sub(r'^[.]+', "", str(running_config))
    startup_config_compareble = re.sub(r'^=== show (external|internal) startup(1|2|3|4) ===', "", str(startup_config))
    return running_config_compareble, startup_config_compareble


def cli_ttysendwaitset_in(ttynum, timeout, nl, cmd):
    return ttysend_input(('ttysendwaitset tty ' + str(ttynum) + ' timeout '
                         + str(timeout) + ' nl ' + nl + ' input'), cmd)


def cli_ttysendwaitset_ctl(ttynum, timeout, nl, ctl):
    return 'ttysendwaitset tty ' + str(ttynum) + ' timeout ' + str(timeout) + ' nl ' + nl + ' ctl_char ' + str(ctl)


def cli_ttysendwaitset_nl(ttynum, timeout, nl):
    return 'ttysendwaitset tty ' + str(ttynum) + ' timeout ' + str(timeout) + ' nl ' + nl + ' nlonly'


def cli_ttysend_delay_in(ttynum, delay, nl, cmd):
    return ttysend_input(('ttysend tty ' + str(ttynum) + ' delay ' + str(delay) + ' nl ' + nl + ' input'), cmd)


def cli_ttysend_delay_ctl(ttynum, delay, nl, ctl):
    return 'ttysend tty ' + str(ttynum) + ' delay ' + str(delay) + ' nl ' + nl + ' ctl_char ' + str(ctl)


def cli_ttysend_delay_nl(ttynum, delay, nl):
    return 'ttysend tty ' + str(ttynum) + ' delay ' + str(delay) + ' nl ' + nl + ' nlonly'


def cli_ttysend_in(ttynum, nl, cmd):
    return ttysend_input(('ttysend tty ' + str(ttynum) + ' nl ' + nl + ' input'), cmd)


def cli_ttysend_ctl(ttynum, nl, ctl):
    return 'ttysend tty ' + str(ttynum) + ' nl ' + nl + ' ctl_char ' + str(ctl)


def cli_ttysend_nl(ttynum, nl):
    return 'ttysend tty ' + str(ttynum) + ' nl ' + nl + ' nlonly'


def ttysend_input(cmd, sendchar):
    return {
        'command': cmd,
        'prompt': 'sendstr> ',
        'answer': '%s\r' % sendchar,
        'newline': False,
    }


def terminal_ttymanage_waitstr_input(index, recvchar):
    return {
        'command': 'terminal ttymanage waitstr %d input' % index,
        'prompt': 'waitstr> ',
        'answer': '%s\r' % recvchar,
        'newline': False,
    }


def terminal_ttymanage_waitregex_input(index, recvchar):
    return {
        'command': 'terminal ttymanage waitregex %d input' % index,
        'prompt': 'waitregex> ',
        'answer': '%s\r' % recvchar,
        'newline': False,
    }


def terminal_ttymanage_errregex_input(index, recvchar):
    return {
        'command': 'terminal ttymanage errorregex %d input' % index,
        'prompt': 'errorregex> ',
        'answer': '%s\r' % recvchar,
        'newline': False,
    }


time_min = 1
time_max = 7200


def check_cmdto(module, cmd_timeout):
    if time_min <= int(cmd_timeout) <= time_max:
        return
    else:
        module.fail_json(
            msg='cmd_timeout parameter %s is invalid. valid range is from %d to %d' %
            (cmd_timeout, time_min, time_max)
        )


def check_recvchar(module, recvchar, chklist, listmax):
    if len(recvchar) <= listmax:
        return
    else:
        module.fail_json(
            msg='%s parameter is invalid. The maximum number of list is %d.' % (chklist, listmax)
        )


NEWLINE = "__NL__"
WAITSEC = "__WAIT__:"
NOWAIT = "__NOWAIT__"
NOWAITSEC = "__NOWAIT__:"
CTLCHAR = "__CTL__:"

ctlchar_list = ['00', '01', '02', '03', '04', '05', '06', '07',
                '08', '09', '0a', '0b', '0c', '0d', '0e', '0f',
                '10', '11', '12', '13', '14', '15', '16', '17',
                '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '7f']


def parse_cmd(module, cmd, spcmd):
    try:
        if spcmd == WAITSEC:
            return cmd.split("__WAIT__:")[0]
        elif spcmd == NOWAIT or spcmd == NOWAITSEC:
            return cmd.split("__NOWAIT__")[0]
        elif spcmd == CTLCHAR:
            ctlchar = str.rstrip(cmd.split("__CTL__:")[1])
            if ctlchar not in ctlchar_list:
                raise Exception
            else:
                return ctlchar
        else:
            pass
    except Exception:
        module.fail_json(msg='invalid sendchar %s.' % cmd)


def parse_optsec(module, cmd, spcmd):
    if spcmd == WAITSEC:
        optsec = cmd.split("__WAIT__:")[1]
    elif spcmd == NOWAITSEC:
        optsec = cmd.split("__NOWAIT__:")[1]
    else:
        pass
    reg = re.compile(r'^[0-9]+$')
    digit = reg.match(optsec)
    if digit:
        optsec = int(optsec)
        if (time_min <= optsec <= time_max):
            return optsec
        else:
            module.fail_json(
                msg='%s%d sec parameter is invalid. valid range is from %d to %d' %
                (spcmd, optsec, time_min, time_max)
            )
    else:
        module.fail_json(msg='invalid sendchar \'%s\'.' % cmd)


def num_range_check(module, optname, num, range_min, range_max):
    if range_min <= num <= range_max:
        return
    else:
        module.fail_json(
            msg='%d is invalid. %s valid range is from %d to %d' %
            (num, optname, range_min, range_max)
        )


def contain_initprompt(module, prompt, response):
    response = flatten(response)
    prompt = prompt.strip()
    try:
        reg = re.compile(r"%s" % prompt)
        matched = reg.search(response[-1])
        if matched:
            return True
        else:
            return False
    except Exception:
        module.fail_json(msg='%s is invalid.' % (prompt))


def pre_check(module):
    if module.params['initial_prompt']:
        return True
    else:
        return False


def pre_action(module):
    tty = module.params['tty']
    nl = module.params['nl']
    initial_prompt = module.params['initial_prompt']
    initial_cmd = module.params['initial_prompt_check_cmd']
    initial_cmd_timeout = module.params['initial_prompt_check_cmd_timeout']
    escape_cmd = module.params['escape_cmd']
    escape_cmd_timeout = module.params['escape_cmd_timeout']
    escape_cmd_retry = module.params['escape_cmd_retry']

    num_range_check(module, 'initial_prompt_check_cmd_timeout', initial_cmd_timeout, 1, 30)
    num_range_check(module, 'escape_cmd_timeout', escape_cmd_timeout, 1, 30)
    num_range_check(module, 'escape_cmd_retry', escape_cmd_retry, 0, 8)

    initial_command = list()
    initial_command.append(get_clicmd_ttysend_delay
                           (module, tty, nl, initial_cmd, initial_cmd_timeout))

    pre_response = list()
    pre_response.append(remove_sendstr(run_commands(module, initial_command)))

    if contain_initprompt(module, initial_prompt, pre_response):
        return flatten(pre_response)

    if escape_cmd is None:
        module.fail_json(
            msg='pre_check failed. \'%s\' was not detect. : %s'
            % (initial_prompt, pre_response)
        )

    for i in range(escape_cmd_retry + 1):
        escape_command = list()
        escape_command.append(
            get_clicmd_ttysend_delay(module, tty, nl, escape_cmd, escape_cmd_timeout)
        )
        pre_response.append(remove_sendstr(run_commands(module, escape_command)))
        if contain_initprompt(module, initial_prompt, pre_response):
            break

        pre_response.append(remove_sendstr(run_commands(module, initial_command)))
        if contain_initprompt(module, initial_prompt, pre_response):
            break

        if escape_cmd_retry == 0:
            module.fail_json(
                msg='pre_check failed. \'%s\' was not detected \
                after sending initial_prompt_check_cmd. : %s'
                % (initial_prompt, pre_response)
            )
        elif i == escape_cmd_retry:
            module.fail_json(
                msg='pre_check failed(retry limit:%d). \'%s\' was not detected \
                after sending initial_prompt_check_cmd. : %s'
                % (escape_cmd_retry, initial_prompt, pre_response)
            )

    return flatten(pre_response)


def comma_and_hyphen_to_comma(s):
    for x in s.split(','):
        elem = x.split('-')
        if len(elem) == 1:
            yield int(elem[0])
        elif len(elem) == 2:
            start, end = list(map(int, elem))
            for i in range(start, end + 1):
                yield i
        else:
            raise ValueError("tty parameter is invalid range. valid range is from 1 to 48")


def change_hyphen_list_to_comma_list(tty):
    ttylist = list(comma_and_hyphen_to_comma(tty))

    if not 1 <= ttylist[0] < 49 or not 1 <= ttylist[-1] < 49:
        raise ValueError("tty parameter is invalid range. valid range is from 1 to 48")
    else:
        return ttylist


def check_return_error(module, responses):
    if module.params['error_detect_on_module'] == "ok":
        return
    else:
        console_output_result = {}
        console_output_result.update({
            'stdout': responses,
            'stdout_lines': list(to_lines(responses))
        })

        resp_list = flatten(list(to_lines(responses)))
        # check error_recvchar_regex error
        if module.params['error_recvchar_regex']:
            r = re.compile("(^|\r|\n)Error:: Matched")
            errrecv_match_result = [i for i in resp_list if r.match(i)]
            if errrecv_match_result:
                module.fail_json(
                    msg='error_recvchar_regex matched %s, console_output: %s' %
                    (errrecv_match_result, console_output_result)
                )

        # check other errors
        r_other = re.compile("(^|\r|\n)Error::")
        errrecv_other_result = [i for i in resp_list if r_other.match(i)]
        if errrecv_other_result:
            module.fail_json(
                msg='Error detect %s, console_output: %s' %
                (errrecv_other_result, console_output_result)
            )


def get_clicmd_ttysend_waitset(module, tty, nl, cmd, cmd_timeout):
    # WAIT__:sec of NO OPTION
    if NEWLINE in cmd:
        return cli_ttysendwaitset_nl(tty, cmd_timeout, nl)
    elif CTLCHAR in cmd:
        ctl = parse_cmd(module, cmd, CTLCHAR)
        return cli_ttysendwaitset_ctl(tty, cmd_timeout, nl, ctl)
    else:
        return cli_ttysendwaitset_in(tty, cmd_timeout, nl, cmd)


def get_clicmd_ttysend_delay(module, tty, nl, cmd, cmd_timeout):
    # __NOWAIT__:sec
    if NEWLINE in cmd:
        return cli_ttysend_delay_nl(tty, cmd_timeout, nl)
    elif CTLCHAR in cmd:
        ctl = parse_cmd(module, cmd, CTLCHAR)
        return cli_ttysend_delay_ctl(tty, cmd_timeout, nl, ctl)
    else:
        return cli_ttysend_delay_in(tty, cmd_timeout, nl, cmd)


def get_clicmd_ttysend(module, tty, nl, cmd):
    # __NOWAIT__
    if NEWLINE in cmd:
        return cli_ttysend_nl(tty, nl)
    elif CTLCHAR in cmd:
        ctl = parse_cmd(module, cmd, CTLCHAR)
        return cli_ttysend_ctl(tty, nl, ctl)
    else:
        return cli_ttysend_in(tty, nl, cmd)


def remove_sendstr(response):
    return [re.sub('sendstr> .*\n', '', s) for s in response]


def edit_responses(module, responses):
    # nl, cmd_timeout, cmd_timeout_onfail
    paramlen_grp1 = 3

    # recvchar
    paramlen_recvchar = \
        len(module.params['recvchar']) if (module.params['recvchar']) else 0

    # recvchar_regex
    paramlen_recvchar_regex = \
        len(module.params['recvchar_regex']) if (module.params['recvchar_regex']) else 0

    # error_recvchar_regex
    paramlen_error_recvchar_regex = \
        len(module.params['error_recvchar_regex']) if (module.params['error_recvchar_regex']) else 0

    # tty
    paramlen_grp2 = 1

    del_idx = (paramlen_grp1
               + paramlen_recvchar
               + paramlen_recvchar_regex
               + paramlen_error_recvchar_regex
               + paramlen_grp2
               )

    del responses[0:(del_idx)]

    responses = [re.sub('sendstr> .*\n', '', s) for s in responses]
    return responses


def mk_response(response, del_nl, del_ll):
    cmd_response = response[1:-1]
    if not del_ll:
        cmd_response.append(response[-1])
    if del_nl:
        cmd_response = ([s for s in cmd_response if s != ''])
    return cmd_response


def custom_responses(module, responses, del_nl, del_ll):
    cstm_resp = []
    for resp in responses:
        cmd_response = mk_response(resp, del_nl, del_ll)
        cmd_result = dict(execute_command=resp[0], response=cmd_response)
        cstm_resp.append(cmd_result)

    return cstm_resp
