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
from delimiter import processors


class ZookeeperQuotaEngine(engine.QuotaEngine):
    """Engine based on zookeeper primitives.

    This engine uses zookeeper transcations, paths and values and versions
    identifiers to ensure a consistent backend storage of user quotas
    and limits on some set of resources.
    """

    processors = {
        'upper_bound': processors.UpperBoundProcessor(),
    }

    def __init__(self, uri):
        super(ZookeeperQuotaEngine, self).__init__(uri)
        if not self.uri.path or self.uri.path == "/":
            raise ValueError("A non-empty url path is required")
        self.client = None

    @property
    def started(self):
        if self.client is None:
            return False
        return self.client.connected

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
                    stored = json.loads(blob)
                    kind = stored['kind']
                    processor = self.processors.get(kind)
                    if not processor:
                        raise ValueError("Read unsupported kind '%s'" % kind)
                    limits.append((resource,
                                   processor.decode(stored['details'])))
            return limits

    def create_or_update_limit(self, for_who, resource,
                               limit, kind='upper_bound'):
        processor = self.processors.get(kind)
        if not processor:
            raise ValueError("Unsupported kind '%s'" % kind)
        who_path = paths.join(self.uri.path, for_who)
        self.client.ensure_path(who_path)
        resource_path = paths.join(who_path, resource)
        try:
            self.client.create(resource_path, json.dumps({
                'kind': kind,
                'details': processor.create(limit),
            }))
        except exceptions.NodeExistsError:
            blob, znode = self.client.get(resource_path)
            stored = json.loads(blob)
            if stored['kind'] != kind:
                raise ValueError("Can only update limits of the same"
                                 " kind, %s != %s" % (kind, stored['kind']))
            else:
                stored['details'] = processor.update(stored['details'], limit)
                # Ensure we pass in the version that we read this on so
                # that if it was changed by some other actor that we can
                # avoid overwriting that value (and retry, or handle in some
                # other manner).
                self.client.set(resource_path, json.dumps(stored),
                                version=znode.version)

    def _try_consume(self, for_who, resource, stored, amount):
        kind = stored['kind']
        processor = self.processors.get(kind)
        if not processor:
            raise ValueError("Unsupported kind '%s' encountered"
                             " for resource '%s' owned by '%s'"
                             % (kind, resource, for_who))
        return processor.process(stored['details'], amount)

    def consume_many(self, for_who, resources, amounts):
        who_path = paths.join(self.uri.path, for_who)
        values_to_save = []
        for resource, amount in zip(resources, amounts):
            resource_path = paths.join(who_path, resource)
            blob, znode = self.client.get(resource_path)
            new_stored = self._try_consume(for_who, resource,
                                           json.loads(blob), amount)
            values_to_save.append((resource_path,
                                   json.dumps(new_stored),
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
        new_stored = self._try_consume(for_who, resource,
                                       json.loads(blob), amount)
        # Ensure we pass in the version that we read this on so
        # that if it was changed by some other actor that we can
        # avoid overwriting that value (and retry, or handle in some
        # other manner).
        self.client.set(resource_path, json.dumps(new_stored),
                        version=znode.version)

    def close(self):
        if self.client is not None:
            self.client.stop()
            self.client.close()
            self.client = None
