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

import json

from kazoo import client
from kazoo import exceptions
from kazoo.protocol import paths

from delimiter import engine


class ZookeeperQuotaEngine(engine.QuotaEngine):
    """Engine based on zookeeper primitives.

    This engine uses zookeeper transcations, paths and values and versions
    identifiers to ensure a consistent backend storage of user quotas
    and limits on some set of resources.
    """

    def __init__(self, uri):
        super(ZookeeperQuotaEngine, self).__init__(uri)
        if not self.uri.path or self.uri.path == "/":
            raise ValueError("A non-empty url path is required")
        self.client = None

    def start(self):
        self.client = client.KazooClient(hosts=self.uri.netloc)
        self.client.start()
        self.client.ensure_path(self.uri.path)

    def read_limits(self, for_who):
        who_path = paths.join(self.uri.path, for_who)
        try:
            child_nodes = self.client.get_children(who_path)
        except exceptions.NoNodeError:
            return []
        else:
            limits = []
            for resource in child_nodes:
                try:
                    blob, _znode = self.client.get(paths.join(who_path,
                                                              resource))
                except exceptions.NoNodeError:
                    pass
                else:
                    limits.append((resource, json.loads(blob)))
            return limits

    def create_or_update_limits(self, for_who, resources, limits):
        who_path = paths.join(self.uri.path, for_who)
        self.client.ensure_path(who_path)
        for resource, limit in zip(resources, limits):
            resource_path = paths.join(who_path, resource)
            try:
                self.client.create(resource_path, json.dumps(limit))
            except exceptions.NodeExistsError:
                blob, znode = self.client.get(resource_path)
                cur_limit = json.loads(blob)
                cur_limit.update(limit)
                # Ensure we pass in the version that we read this on so
                # that if it was changed by some other actor that we can
                # avoid overwriting that value (and retry, or handle in some
                # other manner).
                self.client.set(resource_path, json.dumps(cur_limit),
                                version=znode.version)

    def consume_many(self, for_who, resources, amounts):
        who_path = paths.join(self.uri.path, for_who)
        values_to_save = []
        for resource, amount in zip(resources, amounts):
            resource_path = paths.join(who_path, resource)
            blob, znode = self.client.get(resource_path)
            cur_limit = json.loads(blob)
            try:
                cur_consumed = cur_limit['consumed']
            except KeyError:
                cur_consumed = 0
            max_resource = cur_limit['max']
            if cur_consumed + amount > max_resource:
                raise ValueError("Limit reached, can not"
                                 " consume %s of %s" % (resource, amount))
            else:
                cur_limit['consumed'] = cur_consumed + amount
                values_to_save.append((resource_path,
                                       json.dumps(cur_limit),
                                       znode.version))
        # Commit all changes at once, so that we can ensure that all the
        # changes will happen, or none will...
        if values_to_save:
            with self.client.transaction() as txn:
                for path, value, version in values_to_save:
                    txn.set_data(path, value, version=version)

    def consume(self, for_who, resource, amount):
        who_path = paths.join(self.uri.path, for_who)
        resource_path = paths.join(who_path, resource)
        blob, znode = self.client.get(resource_path)
        cur_limit = json.loads(blob)
        try:
            cur_consumed = cur_limit['consumed']
        except KeyError:
            cur_consumed = 0
        max_resource = cur_limit['max']
        if cur_consumed + amount > max_resource:
            raise ValueError("Limit reached, can not"
                             " consume %s of %s" % (resource, amount))
        else:
            cur_limit['consumed'] = cur_consumed + amount
            # Ensure we pass in the version that we read this on so
            # that if it was changed by some other actor that we can
            # avoid overwriting that value (and retry, or handle in some
            # other manner).
            self.client.set(resource_path, json.dumps(cur_limit),
                            version=znode.version)

    def close(self):
        if self.client is not None:
            self.client.stop()
            self.client.close()
            self.client = None
