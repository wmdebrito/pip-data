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
import xml.dom.minidom as xml
from io import open
import xbmc

u'''
Class Keymap
creates and updates keymap xml file
'''
class Keymap(object):

    # constructor
    def __init__(self, path):
        self.path = path


    # update keys
    def update(self, keyToggle, keyBack, keyUp, keyDown):
        self.keyActions = [
            {u'action': u'toggle_pip',       u'key': keyToggle},
            {u'action': u'channel_back_pip', u'key': keyBack},
            {u'action': u'channel_up_pip',   u'key': keyUp},
            {u'action': u'channel_down_pip', u'key': keyDown}]


    # create keymap xml file
    def create(self):

        # create new xml document
        doc = xml.Document();

        # add root element
        elKeymap = doc.createElement(u'keymap')
        doc.appendChild(elKeymap)

        # create sub elements
        elGlobal = doc.createElement(u'global')
        elKeymap.appendChild(elGlobal)
        elKeyboard = doc.createElement(u'keyboard')
        elGlobal.appendChild(elKeyboard)

        # create sub element to keyboard for each key
        for item in self.keyActions:

            # split setting string
            parts = item[u'key'].split(u'+')

            # create key element
            elKey = doc.createElement(parts[-1])
            elKeyboard.appendChild(elKey)

            # add mod attribute to key element
            if len(parts) > 1:
                elKey.setAttribute(u'mod', u','.join(parts[:-1]))

            # add action content to key element
            elKey.appendChild(doc.createTextNode(u'NotifyAll(service.pip, %s)' % item[u'action']))

        # create xml string
        s = doc.toprettyxml(indent=u"  ", newl=u"\n")

        # write strint to file
        xbmc.log(u'>>>>>>>>>>', xbmc.LOGINFO)
        xbmc.log(u'pipkeymap.xml', xbmc.LOGINFO)
        xbmc.log(self.path, xbmc.LOGINFO)
        fobj = open(self.path + u'/' + u'pipkeymap.xml', u'w')
        fobj.write(s)
        fobj.close()

