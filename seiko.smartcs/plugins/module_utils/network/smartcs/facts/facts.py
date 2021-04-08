#
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Seiko Solutions Inc. all rights reserved.
#
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The facts class for smartcs
this file validates each subset of facts and selectively
calls the appropriate facts gathering function
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)
from ansible_collections.seiko.smartcs.plugins.module_utils.network.smartcs.facts.legacy.base import (
    Default,
    Tty,
    Config,
)


FACT_LEGACY_SUBSETS = dict(
    default=Default,
    tty=Tty,
    config=Config,
)

FACT_RESOURCE_SUBSETS = dict(
)


class Facts(FactsBase):
    """ The fact class for smartcs
    """

    VALID_LEGACY_GATHER_SUBSETS = frozenset(FACT_LEGACY_SUBSETS.keys())

    def __init__(self, module):
        super(Facts, self).__init__(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        """ Collect the facts for smartcs
        :param legacy_facts_type: List of legacy facts types
        :param resource_facts_type: List of resource fact types
        :param data: previously collected conf
        :rtype: dict
        :return: the facts gathered
        """

        if self.VALID_LEGACY_GATHER_SUBSETS:
            self.get_network_legacy_facts(FACT_LEGACY_SUBSETS, legacy_facts_type)

        return self.ansible_facts, self._warnings
