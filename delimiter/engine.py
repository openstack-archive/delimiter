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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class QuotaEngine(object):
    """The abstraction that all quota engines derive from."""

    def __init__(self, uri):
        self.uri = uri

    def start(self):
        """Performs any engine startup (connection setup, validation...)"""

    def close(self):
        """Performs engine teardown (connection closing...)"""

    @abc.abstractmethod
    def read_limits(self, for_who):
        """Reads the limits of some entity."""

    @abc.abstractmethod
    def create_or_update_limit(self, for_who, resource, limit):
        """Updates or creates a resource limit for some entity.

        Must operate transactionally; either created/updated or not.
        """

    @abc.abstractmethod
    def consume_many(self, for_who, resources, amounts):
        """Consumes a given amount of resources for some entity.

        Must operate transactionally; either all consumed or none.
        """

    @abc.abstractmethod
    def consume(self, for_who, resource, amount):
        """Consumes a amount of resource for some entity.

        Must operate transactionally; either consumed or not.
        """
