# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Seiko Solutions Inc. all rights reserved.
#
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The smartcs legacy fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import platform
import re

from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.smartcs import (
    run_commands,
    get_capabilities,
)

from ansible.module_utils.six.moves import zip


class FactsBase(object):

    COMMANDS = list()

    def __init__(self, module):
        self.module = module
        self.facts = dict()
        self.warnings = list()
        self.responses = None

    def populate(self):
        self.responses = run_commands(self.module, commands=self.COMMANDS, check_rc=False)

    def run(self, cmd):
        return run_commands(self.module, commands=cmd, check_rc=False)


class Default(FactsBase):

    COMMANDS = [
        'show version',
        'show ip',
        'show ipinterface bond1',
        'show ipinterface eth1',
        'show ipinterface eth2'
    ]

    def populate(self):
        super(Default, self).populate()
        shver = self.responses[0]
        ship = self.responses[1]
        shifb1 = self.responses[2]
        shife1 = self.responses[3]
        shife2 = self.responses[4]

        if shver:
            self.facts['version'] = self.parse_version(shver)
            self.facts['serialnum'] = self.parse_serialnum(shver)
            self.facts['model'] = self.parse_model(shver)
            self.facts['mainsystem'] = self.parse_mainsystem(shver)
            self.facts['backupsystem'] = self.parse_backupsystem(shver)
            self.facts['bootrom'] = self.parse_bootrom(shver)
            self.facts['bootconfig'] = self.parse_bootconfig(shver)

        if ship:
            self.facts['hostname'] = self.parse_hostname(ship)
            self.facts['eth1'] = self.parse_eth1(ship)
            self.facts['eth2'] = self.parse_eth2(ship)
            self.facts['bond1'] = self.parse_bond1(ship)

        if shifb1:
            self.facts['bond1'] = dict(
                v4_ip=self.parse_v4ip(shifb1),
                v4_mask=self.parse_v4mask(shifb1),
                v6_ip=self.parse_v6ip(shifb1),
                v6_mask=self.parse_v6mask(shifb1),
                v6_linklocal_ip=self.parse_v6llip(shifb1),
                v6_linklocal_mask=self.parse_v6llmask(shifb1)
            )

        if shife1:
            self.facts['eth1'] = dict(
                v4_ip=self.parse_v4ip(shife1),
                v4_mask=self.parse_v4mask(shife1),
                v6_ip=self.parse_v6ip(shife1),
                v6_mask=self.parse_v6mask(shife1),
                v6_linklocal_ip=self.parse_v6llip(shife1),
                v6_linklocal_mask=self.parse_v6llmask(shife1)
            )

        if shife2:
            self.facts['eth2'] = dict(
                v4_ip=self.parse_v4ip(shife2),
                v4_mask=self.parse_v4mask(shife2),
                v6_ip=self.parse_v6ip(shife2),
                v6_mask=self.parse_v6mask(shife2),
                v6_linklocal_ip=self.parse_v6llip(shife2),
                v6_linklocal_mask=self.parse_v6llmask(shife2)
            )

    def platform_facts(self):
        platform_facts = {}

        resp = get_capabilities(self.module)
        device_info = resp['device_info']

        platform_facts['system'] = device_info['network_os']

        for item in ('model', 'image', 'version', 'platform', 'hostname'):
            val = device_info.get('network_os_%s' % item)
            if val:
                platform_facts[item] = val

        platform_facts['api'] = resp['network_api']
        platform_facts['python_version'] = platform.python_version()

        return platform_facts

    def parse_version(self, data):
        match = re.search(r'System                : System Software Ver (.*)', data)
        if match:
            return match.group(1)

    def parse_serialnum(self, data):
        match = re.search(r'Serial No.            : (.*)', data)
        if match:
            return match.group(1)

    def parse_model(self, data):
        match = re.search(r'Model                 : (.*)', data)
        if match:
            return match.group(1)

    def parse_mainsystem(self, data):
        match = re.search(r'Main System           : Ver (.*)', data)
        if match:
            return match.group(1)

    def parse_backupsystem(self, data):
        match = re.search(r'Backup System         : Ver (.*)', data)
        if match:
            return match.group(1)

    def parse_bootrom(self, data):
        match = re.search(r'BootROM               : Ver (.*)', data)
        if match:
            return match.group(1)

    def parse_bootconfig(self, data):
        match = re.search(r'Boot Config           : (.*)', data)
        if match:
            return match.group(1)

    def parse_hostname(self, data):
        match = re.search(r'Hostname         : (.+)', data)
        if match:
            return match.group(1)

    def parse_eth1(self, data):
        match = re.search(r'IPaddress\(eth1\)  : (.+)', data)
        if match:
            return match.group(1)

    def parse_eth2(self, data):
        match = re.search(r'IPaddress\(eth2\)  : (.+)', data)
        if match:
            return match.group(1)

    def parse_bond1(self, data):
        match = re.search(r'IPaddress\(bond1\) : (.+)', data)
        if match:
            return match.group(1)

    def parse_v4ip(self, data):
        match = re.search(r' (bond1|eth1|eth2)(.*)(up|down)(.*)([1-9].+)(.*)static  (.*)/(.*)', data)
        if match and '.' in match.group(7):
            return match.group(7)

    def parse_v4mask(self, data):
        match = re.search(r' (bond1|eth1|eth2)(.*)(up|down)(.*)([1-9].+)(.*)static  (.*)/(.*)', data)
        if match and '.' in match.group(7):
            return match.group(8)

    def parse_v6ip(self, data):
        match1 = re.search(r' (bond1|eth1|eth2)(.*)(up|down)(.*)([1-9].+)(.*)static  (.*)/(.*)', data)
        match2 = re.search(r'                    static  (.+)/(.+)', data)
        if match1 and ':' in match1.group(7):
            return match1.group(7)
        if match2:
            return match2.group(1)

    def parse_v6mask(self, data):
        match1 = re.search(r' (bond1|eth1|eth2)(.*)(up|down)(.*)([1-9].+)(.*)static  (.*)/(.*)', data)
        match2 = re.search(r'                    static  (.+)/(.+)', data)
        if match1 and ':' in match1.group(7):
            return match1.group(8)
        if match2:
            return match2.group(2)

    def parse_v6llip(self, data):
        match1 = re.search(r' (bond1|eth1|eth2)(.*)(up|down)(.*)([1-9].+)(.*)link    (.*)/(.*)', data)
        match2 = re.search(r'                    link    (.+)/(.+)', data)
        if match1:
            return match1.group(7)
        if match2:
            return match2.group(1)

    def parse_v6llmask(self, data):
        match1 = re.search(r' (bond1|eth1|eth2)(.*)(up|down)(.*)([1-9].+)(.*)link    (.*)/(.*)', data)
        match2 = re.search(r'                    link    (.+)/(.+)', data)
        if match1:
            return match1.group(8)
        if match2:
            return match2.group(2)


class Config(FactsBase):

    COMMANDS = [
        'show config running all'
        # 'show config running system',
        # 'show config running ether',
        # 'show config running bonding',
        # 'show config running ip',
        # 'show config running ip6',
        # 'show config running user',
        # 'show config running ipinterface',
        # 'show config running ip host',
        # 'show config running ip route',
        # 'show config running ip6route',
        # 'show config running ipfilter',
        # 'show config running ipsec',
        # 'show config running dns',
        # 'show config running syslog',
        # 'show config running sntp',
        # 'show config running nfs',
        # 'show config running auth',
        # 'show config running acct',
        # 'show config running portd',
        # 'show config running tty',
        # 'show config running logd',
        # 'show config running console',
        # 'show config running temperature',
        # 'show config running snmp',
        # 'show config running service',
        # 'show config running maintenance',
        # 'show config running terminal',
    ]

    def populate(self):
        super(Config, self).populate()
        data = self.responses[0]
        if data:
            self.facts['config'] = data


class Tty(FactsBase):

    COMMANDS = [
        'show portd tty',
        'show tty'
    ]

    def populate(self):
        super(Tty, self).populate()

        shportd = "\n" + self.responses[0]
        shtty = self.responses[1]
        entries = []

        for shportd_line, shtty_line in zip(shportd.split('\n'), shtty.split('\n')):
            portd_match = re.search(
                r'(\d+)\s+(.+)\s+(\d)\s+(\d)\s+(both|tel|ssh)\s+(both|rw|ro)\s+(ssh|-)\s+(on|off)\s+(.+)\s+(cr|lf|crlf)\s+(.+)\s+(cr|lf|crlf|-)',
                shportd_line
            )
            tty_match = re.search(
                r'(\d+)\s+(.+)\s+(\d)\s+(none|even|odd)\s+(1|2)\s+(none|rts|xon)\s+(on|off)',
                shtty_line
            )
            if portd_match and tty_match:
                entry = dict(
                    tty=int(tty_match.group(1)),
                    label=portd_match.group(2).strip(),
                    baud=int(tty_match.group(2)),
                    bitchar=int(tty_match.group(3)),
                    parity=tty_match.group(4),
                    stop=int(tty_match.group(5)),
                    flow=tty_match.group(6),
                )
                if entry:
                    entries.append(entry)

        self.facts['tty'] = entries
