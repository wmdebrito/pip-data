#!/usr/bin/python

u'''
Copyright (C) 2021 mltobi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

from __future__ import absolute_import
import xbmc

import json


u'''
Class M3u
handles m3u download, parsing and url request
'''
class M3u(object):

    # constructor
    def __init__(self, username, password, ipaddress, port, profile):
        self.update_settings(username, password, ipaddress, port, profile)
        self.m3ulines = None
        self.channel2url = {}
        self.channel2number = {}
        self.number2channel = {}
        self.number2url = {}
        self.channel2id = {}
        self.url = u""
        self.channel = u""


    # update settings
    def update_settings(self, username, password, ipaddress, port, profile):
        self.username = username
        self.password = password
        self.ipaddress = ipaddress
        self.port = port
        self.profile = profile


    # download m3u as pipe from tvheadend server
    def download(self):
        self.m3ulines =  open("/storage/kodi/kodi.m3u", "r").read().decode(u"utf-8").split(u"\n")
        xbmc.log(u"[pip-service] self.m3ulines: %d" % len(self.m3ulines), xbmc.LOGINFO)


    # parse m3u file to dict
    def parse(self):

        # #EXTINF:-1 logo="http://192.168.144.67:9981/imagecache/13" tvg-id="efa6b645f9399cc41becd20cceb0d2c2" tvg-chno="1",Das Erste HD
        # http://192.168.144.67:9981/stream/channelid/1169598191?profile=pass

        self.channel2url = {}
        self.channel2number = {}
        self.number2url = {}
        self.number2channel = {}
        if self.m3ulines != None:
            for i, line in enumerate(self.m3ulines):
                # loop line list
                if line.find(u"logo=") != -1 and line.find(u"group-title=") != -1:
                    # split line by tvg-chno
                    parts = line.split(u"group-title=")

                    if len(parts) > 1:
                        # split line by '",' to get channel name
                        pparts = parts[1].split(u"\",")

                        if len(pparts) > 1:
                            # create a loopup dictionary key=channel-name and value=url-link
                            name = pparts[1].replace(u'\n', u'')
                            self.channel2url[name] = self.m3ulines[i+1].replace(u'\n', u'')

                            # create a loopup dictionary key=channel-name and value=number
                            number = pparts[0].replace(u'"', u'')
                            self.channel2number[name] = int(number)
                            self.number2channel[int(number)] = name
                            self.number2url[int(number)] = self.channel2url[name]

            xbmc.log(u"[pip-service] parsed %d channels." % len(self.channel2url), xbmc.LOGINFO)
            if len(self.channel2url) == 0:
                xbmc.log(u"[pip-service] check m3u file format to be:", xbmc.LOGDEBUG)
                xbmc.log(u"[pip-service] #EXTINF:-1 logo=\"...\" tvg-id=\"...\" tvg-chno=\"...\",[channel name]", xbmc.LOGDEBUG)
                xbmc.log(u"[pip-service] http://192.168.1.1:9981/stream/channelid/[....]?profile=%s" % self.profile, xbmc.LOGDEBUG)


    # get pip channel name
    def get_channel_name(self):
        return self.channel


    # set new channel name depending on channel number
    def set_channel_name(self, channelnumber):
        self.channel = self.number2channel[channelnumber]


    # get current active channel the url of it
    def get_url(self):

        # get information for current player item as json reponse
        rpccmd = {
          u"jsonrpc": u"2.0",
          u"method": u"Player.GetItem",
          u"params": {
            u"properties": [u"art", u"title", u"album", u"artist", u"season", u"episode", u"duration",
                            u"showtitle", u"tvshowid", u"thumbnail", u"file", u"fanart",u"streamdetails"],
            u"playerid": 1 },
          u"id": u"OnPlayGetItem"}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        try:
            # if a channel label exists create a new channel.pip file that contains the url link
            self.channel = result[u'result'][u'item'][u'label']
            self.url = self.channel2url[self.channel]

        except KeyError:
            self.url = u""

        return self.url, self.channel


    # get all channel ids
    def get_channel_ids(self):

        rpccmd = {u"jsonrpc":u"2.0",u"method": u"PVR.GetChannels",u"params": {u"channelgroupid": u"alltv"},u"id": 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        channels = result[u'result'][u'channels']
        self.channel2id = {}
        for channel in channels:
            self.channel2id[channel[u'label']] = channel[u'channelid']


    # switch to channel
    def switch_channel(self, channelname):

        # get information for current player item as json reponse
        rpccmd = {u"id" : 1,
                  u"jsonrpc" : u"2.0",
                  u"method" : u"Player.Open",
                  u"params" : {
                      u"item" : { u"channelid" : self.channel2id[channelname] }
                   }
                 }
        rpccmd = json.dumps(rpccmd)
        xbmc.executeJSONRPC(rpccmd)
