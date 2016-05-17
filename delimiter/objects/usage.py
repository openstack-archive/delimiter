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


class Usage(object):
    """Represent a resource usage.

    """

    def __init__(self, resource, category, usage=0):
        """Initialize a Usage.

        :param resource: The Resource the usage is for.
        :param category: The category of the Usage.
                          relevant to service users.
        :param usage: The current amount of the resource which is in
                      use by the user.

        """

        self.resource = resource
        self.category = category
        self.usage = usage
