# -*- coding: utf-8 -*-

#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections

from delimiter import exceptions


BoundedResource = collections.namedtuple('BoundedResource',
                                         ['consumed', 'bound'])


class UpperBoundProcessor(object):
    """Processes a limit given some upper bound."""

    @staticmethod
    def create(limit):
        """Given some limit, turn it into a *internal* details dict."""
        return {
            'consumed': 0,
            'bound': limit,
        }

    @staticmethod
    def decode(details):
        """Turn a internal details dict into a user-viewable one."""
        return BoundedResource(details['consumed'], details['bound'])

    @staticmethod
    def update(details, limit):
        """Given internal details dict update it with the given limit."""
        details = details.copy()
        details['bound'] = limit
        return details

    @staticmethod
    def process(details, amount):
        """Given internal details dict process the amount given (or die).

        Updates (and returns) the internal details dict if
        successful (otherwise raises some exception).
        """
        consumed = details['consumed']
        if consumed + amount > details['bound']:
            raise exceptions.OverLimitException(
                "Limit of '%s' can not be passed" % details['bound'])
        else:
            details = details.copy()
            details['consumed'] = consumed + amount
            return details
