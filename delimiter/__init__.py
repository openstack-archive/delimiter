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

from oslo_utils import netutils
import stevedore.driver

ENGINE_NAMESPACE = "delimiter.engines"
DEFAULT_KIND = "sql"


def create_engine(uri):
    """Create a new ``Engine`` instance."""
    parsed_uri = netutils.urlsplit(uri, scheme=DEFAULT_KIND)
    kind = parsed_uri.scheme
    try:
        mgr = stevedore.driver.DriverManager(
            ENGINE_NAMESPACE, kind,
            invoke_on_load=True,
            invoke_args=[parsed_uri])
        engine = mgr.driver
    except RuntimeError:
        raise ValueError("Could not find"
                         "engine '%s' (from uri '%s')" % (kind, uri))
    else:
        return engine
