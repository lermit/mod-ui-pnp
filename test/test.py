#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2012:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit test for GraphiteWebui module.
"""
import unittest
import time

from shinken.objects import Module, Service, Host, Command
from module.module import get_instance


GRAPHEND = time.time()-3600
GRAPHSTART = GRAPHEND-3600

def init_module():
    """Initialize the module with standard configuration"""
    config_options = Module({
        'module_name': 'ui-pnp',
        'module_type': 'pnp_webui',
        'uri': 'http://YOURSERVERNAME/pnp4nagios/',
    })
    return get_instance(config_options)

def init_service(params={}):
    """Create a service with specified parameters

    Parameters
    * params : A dict of parms
        * command_name : The command name (default dummy_cmd)
        * command_line : The command line (default dummy_cmd!1)
        * host_name : The host name (default Dummy host)
        * service_description: The service name (default Dummy service)
        * perf_data : The service perf data (default empty)
    """

    command_name = params.get('command_name', 'dummy_cmd')
    command_line = params.get('command_line', 'dummy_cmd!1')
    host_name = params.get('host_name', 'Dummy host')
    service_description = params.get('service_description', 'Dummy service')
    perf_data = params.get('perf_data', '')

    host = Host({
        'host_name': host_name,
    })

    cmd = Command({
        'command_name': command_name,
        'command_line': command_line,
    })

    srv = Service({
        'service_description': service_description,
        'perf_data': perf_data,
    })
    srv.host = host
    srv.check_command = cmd

    return srv

class ReplaceGraphSizeTest(unittest.TestCase):
    """Test the replacement of graph size"""

    def test_replace_graph_size(self):
        """Test the replace with already specified graph size in url"""

        module = init_module()
        url = 'http://pnp.example.com/?graph_width=42&graph_height=42&after=2'
        new_height = '123'
        new_width = '123'

        new_url = module.replace_graph_size(url, new_width, new_height)
        self.assertIn('graph_height=123', new_url)
        self.assertIn('graph_width=123', new_url)
        self.assertIn('after=2', new_url)

    def test_add_graph_size(self):
        """Test the adding of new graph size"""

        module = init_module()
        url = 'http://pnp.example.com/?before=1&after=2'
        new_height = '123'
        new_width = '123'

        new_url = module.replace_graph_size(url, new_width, new_height)
        self.assertIn('graph_height=123', new_url)
        self.assertIn('graph_width=123', new_url)
        self.assertIn('before=1', new_url)
        self.assertIn('after=2', new_url)

    def test_add_graph_size_height(self):
        """Test adding height graph size"""

        module = init_module()
        url = 'http://pnp.example.com/?before=1&graph_width=42&after=2'
        new_height = '123'
        new_width = '123'

        new_url = module.replace_graph_size(url, new_width, new_height)
        self.assertIn('graph_width=123', new_url)
        self.assertIn('graph_height=123', new_url)
        self.assertIn('before=1', new_url)
        self.assertIn('after=2', new_url)

    def test_add_graph_size_width(self):
        """Test adding width graph size"""

        module = init_module()
        url = 'http://pnp.example.com/?before=1&graph_height=42&after=2'
        new_height = '123'
        new_width = '123'

        new_url = module.replace_graph_size(url, new_width, new_height)
        self.assertIn('graph_height=123', new_url)
        self.assertIn('graph_width=123', new_url)
        self.assertIn('before=1', new_url)
        self.assertIn('after=2', new_url)

class GetGraphUrisTest(unittest.TestCase):
    """Test the get_graph_uris function"""

    def test_service_uri_without_graph(self):
        """Get a simple service graph uri with no graph"""
        module = init_module()
        service = init_service()

        uris = module.get_graph_uris(service, GRAPHSTART, GRAPHEND)

        self.assertIs(type(uris), list)
        self.assertEquals(len(uris), 0)

    def test_service_with_graph(self):
        """Get a simple service with one graph"""
        module = init_module()
        service = init_service({
            'perf_data': 'dummy_service=500M;300;400;110;1000;',
        })

        uris = module.get_graph_uris(
            service,
            GRAPHSTART,
            GRAPHEND)

        self.assertIs(type(uris), list)
        self.assertEquals(len(uris), 1)

    def test_serice_with_graph_size(self):
        """Get a graph with a speicified size"""
        module = init_module()
        service = init_service({
            'perf_data': 'dummy_service=500M;300;400;110;1000;',
        })
        graph_size = {
            'width': '42',
            'height': '4242',
        }

        uris = module.get_graph_uris(
            service,
            GRAPHSTART,
            GRAPHEND,
            params=graph_size)
        img_src = uris[0]['img_src']

        self.assertIn('graph_width=42', img_src)
        self.assertIn('graph_height=4242', img_src)

if __name__ == '__main__':
    unittest.main()
