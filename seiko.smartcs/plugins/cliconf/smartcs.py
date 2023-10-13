#
# Copyright (c) 2021 Seiko Solutions Inc. all rights reserved.
#
# (c) 2017 Red Hat Inc.
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
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
author: "Seiko Solutions Inc. (@naka-shin1)"
name: smartcs
short_description: Use smartcs cliconf to run command on SmartCS platform
description:
- This smartcs plugin provides low level abstraction apis for sending and receiving CLI
  commands from SmartCS devices.
version_added: 1.3.0
"""

import re
import time
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    @enable_mode
    def get_config(self, source='running', flags=None, format=None):
        if source not in ('running', 'startup'):
            raise ValueError("fetching configuration from %s is not supported" % source)

        if format:
            raise ValueError("'format' value %s is not supported for get_config" % format)

        if not flags:
            flags = []
        if source == 'running':
            cmd = 'show config running '
        else:
            cmd = 'show config startup '

        cmd += ' '.join(to_list(flags))
        cmd = cmd.strip()

        return self.send_command(cmd)

    def get_diff(self, candidate=None, running=None, diff_match='line', diff_ignore_lines=None, path=None, diff_replace=None):
        diff = {}
        device_operations = self.get_device_operations()
        option_values = self.get_option_values()

        if candidate is None and device_operations['supports_generate_diff']:
            raise ValueError("candidate configuration is required to generate diff")

        if diff_match not in option_values['diff_match']:
            raise ValueError("'match' value %s in invalid, valid values are %s" % (diff_match, ', '.join(option_values['diff_match'])))

        if diff_replace:
            raise ValueError("'replace' in diff is not supported")

        if diff_ignore_lines:
            raise ValueError("'diff_ignore_lines' in diff is not supported")

        if path:
            raise ValueError("'path' in diff is not supported")

        # prepare candidate configuration
        candidate_obj = NetworkConfig(indent=1)
        want_src, want_banners = self._extract_banners(candidate)
        candidate_obj.load(want_src)

        if running and diff_match != 'none':
            # running configuration
            have_src, have_banners = self._extract_banners(running)
            running_obj = NetworkConfig(indent=1, contents=have_src, ignore_lines=diff_ignore_lines)
            configdiffobjs = candidate_obj.difference(running_obj, path=path, match=diff_match, replace=diff_replace)

        else:
            configdiffobjs = candidate_obj.items
            have_banners = {}

        diff['config_diff'] = dumps(configdiffobjs, 'commands') if configdiffobjs else ''
        banners = self._diff_banners(want_banners, have_banners)
        diff['banner_diff'] = banners if banners else {}
        return diff

    @enable_mode
    def edit_config(self, candidate=None, commit=True, replace=None, comment=None):
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(operations, candidate, commit, replace, comment)

        results = []
        requests = []
        if commit:
            for line in to_list(candidate):
                if not isinstance(line, Mapping):
                    line = {'command': line}

                cmd = line['command']
                if cmd != 'end' and cmd[0] != '!':
                    results.append(self.send_command(**line))
                    requests.append(cmd)
        else:
            raise ValueError('check mode is not supported')

        resp['request'] = requests
        resp['response'] = results
        return resp

    def edit_macro(self, candidate=None, commit=True, replace=None, comment=None):
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capabiltiy(operations, candidate, commit, replace, comment)

        results = []
        requests = []
        if commit:
            commands = ''
            for line in candidate:
                if line != 'None':
                    commands += (' ' + line + '\n')
                obj = {'command': commands, 'sendonly': True}
                results.append(self.send_command(**obj))
                requests.append(commands)

            time.sleep(0.1)
            results.append(self.send_command('\n'))
            requests.append('\n')

        resp['request'] = requests
        resp['response'] = results
        return resp

    def get(self, command=None, prompt=None, answer=None, sendonly=False, output=None, check_all=False):
        if not command:
            raise ValueError('must provide value of command to execute')
        if output:
            raise ValueError("'output' value %s is not supported for get" % output)

        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, check_all=check_all)

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'smartcs'
        reply = self.get(command='show version')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'System                : System Software Ver (.*)', data)
        if match:
            device_info['network_os_version'] = match.group(1).strip(',')

        match = re.search(r'Model                 : (.*)', data)
        if match:
            device_info['network_model'] = match.group(1)

        return device_info

    def get_device_operations(self):
        return {
            'supports_diff_replace': False,
            'supports_commit': False,
            'supports_rollback': False,
            'supports_defaults': True,
            'supports_onbox_diff': False,
            'supports_commit_comment': False,
            'supports_multiline_delimiter': False,
            'supports_diff_match': True,
            'supports_diff_ignore_lines': False,
            'supports_generate_diff': True,
            'supports_replace': False
        }

    def get_option_values(self):
        return {
            'format': ['text'],
            'diff_match': ['line', 'none'],
            'diff_replace': [],
            'output': []
        }

    def get_capabilities(self):
        result = dict()
        result['rpc'] = self.get_base_rpc() + ['edit_banner', 'get_diff', 'run_commands', 'get_defaults_flag']
        result['network_api'] = 'cliconf'
        result['device_info'] = self.get_device_info()
        result['device_operations'] = self.get_device_operations()
        result.update(self.get_option_values())
        return json.dumps(result)

    def edit_banner(self, candidate=None, multiline_delimiter=None, commit=True):
        """
        Edit banner on remote device
        :param banners: Banners to be loaded in json format
        :param multiline_delimiter: Line delimiter for banner
        :param commit: Boolean value that indicates if the device candidate
               configuration should be  pushed in the running configuration or discarded.
        :param diff: Boolean flag to indicate if configuration that is applied on remote host should
                     generated and returned in response or not
        :return: Returns response of executing the configuration command received
             from remote host
        """
        resp = {}
        banners_obj = json.loads(candidate)
        results = []
        requests = []
        if commit:
            for key, value in iteritems(banners_obj):
                for cmd in [key, value]:
                    obj = {'command': cmd, 'sendonly': True}
                    results.append(self.send_command(**obj))
                    requests.append(cmd)

                time.sleep(0.1)
                results.append(self.send_command('\n'))
                requests.append('\n')

        resp['request'] = requests
        resp['response'] = results

        return resp

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {'command': cmd}

            output = cmd.pop('output', None)
            if output:
                raise ValueError("'output' value %s is not supported for run_commands" % output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, 'err', to_text(e))

            responses.append(out)

        return responses

    def get_defaults_flag(self):
        """
        The method identifies the filter that should be used to fetch running-configuration
        with defaults.
        :return: valid default filter
        """
        out = self.get('show config running ?')
        out = to_text(out, errors='surrogate_then_replace')

        commands = set()
        for line in out.splitlines():
            if line.strip():
                commands.add(line.strip().split()[0])

        if 'all' in commands:
            return 'all'
        else:
            return 'full'

    def _extract_banners(self, config):
        banners = {}
        banner_cmds = re.findall(r'^banner (\w+)', config, re.M)
        for cmd in banner_cmds:
            regex = r'banner %s \^C(.+?)(?=\^C)' % cmd
            match = re.search(regex, config, re.S)
            if match:
                key = 'banner %s' % cmd
                banners[key] = match.group(1).strip()

        for cmd in banner_cmds:
            regex = r'banner %s \^C(.+?)(?=\^C)' % cmd
            match = re.search(regex, config, re.S)
            if match:
                config = config.replace(str(match.group(1)), '')

        config = re.sub(r'banner \w+ \^C\^C', '!! banner removed', config)
        return config, banners

    def _diff_banners(self, want, have):
        candidate = {}
        for key, value in iteritems(want):
            if value != have.get(key):
                candidate[key] = value
        return candidate
