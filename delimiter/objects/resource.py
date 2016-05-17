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


class Resource(object):
    """Represent a resource.

    """

    def __init__(self, service, name, params=None):
        """Initialize a Resource

        :param service: The Service object the resource is associated
                        with.
        :param name: The name of the resource, as a string; e.g.,
                     "instances", "vcpus", "images", etc.
        :param params: The names of the parameters necessary to
                       identify the resource.

        """
        self.service = service
        self.name = name
        self.params = set(params) if params else set()
