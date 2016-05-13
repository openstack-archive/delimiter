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


class UpperBoundProcessor(object):
    """Processes a limit given some upper bound."""

    def create(self, bound):
        return {
            'consumed': 0,
            'bound': bound,
        }

    def decode(self, details):
        return details

    def update(self, details, bound):
        details = details.copy()
        details['bound'] = bound
        return details

    def process(self, details, amount):
        consumed = details['consumed']
        if consumed + amount > details['bound']:
            return False
        else:
            details = details.copy()
            details['consumed'] = consumed + amount
            return True
