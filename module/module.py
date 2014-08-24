#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2014:
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
This class is for linking the WebUI with PNP,
for mainly get graphs and links.
"""

import socket, re

from shinken.log import logger
from shinken.basemodule import BaseModule

properties = {
    'daemons': ['webui'],
    'type': 'pnp_webui'
    }

def get_instance(plugin):
    """called by the plugin manager"""
    logger.info("Get an PNP UI module for plugin %s" % plugin.get_name())

    instance = PNPWebui(plugin)
    return instance


class PNPWebui(BaseModule):
    """Main module class"""
    def __init__(self, modconf):
        BaseModule.__init__(self, modconf)
        self.uri = getattr(modconf, 'uri', None)
        self.username = getattr(modconf, 'username', None)
        self.password = getattr(modconf, 'password', '')

        if not self.uri:
            raise Exception('The WebUI PNP module is missing uri parameter.')

        self.uri = self.uri.strip()
        if not self.uri.endswith('/'):
            self.uri += '/'

        # Change YOURSERVERNAME by our server name if we got it
        if 'YOURSERVERNAME' in self.uri:
            my_name = socket.gethostname()
            self.uri = self.uri.replace('YOURSERVERNAME', my_name)

    # Try to connect if we got true parameter
    def init(self):
        pass

    def load(self, app):
        """To load the webui application"""
        self.app = app

    @staticmethod
    def get_number_of_metrics(elt):
        """For an element, give the number of elements in
        the perf_data"""
        perf_data = elt.perf_data.strip()
        elts = perf_data.split(' ')
        elts = [e for e in elts if e != '']
        return len(elts)

    @staticmethod
    def replace_graph_size(url, width, height):
        """Private function to replace the graph size by the specified
        value."""

        # Replace width
        if re.search('graph_width=', url) is None:
            url = "{url}&graph_width={width}".format(
                url=url,
                width=width)
        else:
            url = re.sub(
                r'graph_width=[^\&]+',
                'graph_width={width}'.format(width=width),
                url)

        # Replace Height
        if re.search('graph_height=', url) is None:
            url = "{url}&graph_height={height}".format(
                url=url,
                height=height)
        else:
            url = re.sub(
                r'graph_height=[^\&]+',
                'graph_height={height}'.format(height=height),
                url)

        return url

    def get_external_ui_link(self):
        """Give the link for the PNP UI, with a Name"""
        return {'label': 'PNP4', 'uri': self.uri}

    def get_graph_uris(self, elt, graphstart, graphend,
                       source='detail', params={}):
        """Ask for an host or a service the graph UI that the UI should
        give to get the graph image link and PNP page link too.
        for now, the source variable does nothing. Values passed to this
        variable can be :
            'detail' for the element detail page
            'dashboard' for the dashboard widget
        you can customize the url depending on this value. (or not)

        Parameters
        * params : array of extra parameter :
            * width: graph width (default 586)
            * height: graph height (default 308)
        """
        if not elt:
            return []

        width = params.get('width', 586)
        height = params.get('height', 308)

        my_type = elt.__class__.my_type
        ret = []

        # Generate IMG SRC prefix
        img_src_pre = '{uri}{path}&start={start_date}&end={end_date}'.format(
            uri=self.uri,
            path='index.php/image?view=0',
            start_date=graphstart,
            end_date=graphend)

        # Generate link prefix
        link_pre = '{uri}index.php/graph?'.format(
            uri=self.uri)

        if my_type == 'host':
            nb_metrics = self.get_number_of_metrics(elt)
            for i in range(nb_metrics):
                value = {}
                value['link'] = '{uri}host={host}&srv=_HOST_'.format(
                    uri=link_pre,
                    host=elt.get_name())
                value['img_src'] = '{uri}&source={source}'.format(
                    uri=img_src_pre,
                    source=i)
                value['img_src'] = '{uri}&host={host}&srv=_HOST_'.format(
                    uri=value['img_src'],
                    host=elt.get_name())
                ret.append(value)
                value['img_src'] = self.replace_graph_size(
                    value['img_src'],
                    width,
                    height)
            return ret
        if my_type == 'service':
            nb_metrics = self.get_number_of_metrics(elt)
            for i in range(nb_metrics):
                value = {}
                value['link'] = '{uri}host={host}&srv={srv}'.format(
                    uri=link_pre,
                    host=elt.host.host_name,
                    srv=elt.service_description)
                value['img_src'] = "{uri}&source={source}".format(
                    uri=img_src_pre,
                    source=i)
                value['img_src'] = "{uri}&host={host}&srv={srv}".format(
                    uri=value['img_src'],
                    host=elt.host.host_name,
                    srv=elt.service_description)
                value['img_src'] = self.replace_graph_size(
                    value['img_src'],
                    width,
                    height)
                ret.append(value)
            return ret

        # Oups, bad type?
        return []
