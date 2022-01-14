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
import xbmcgui
import xbmcaddon

import os
import shutil
import uuid
import platform
#from io import open


u'''
Class Pip
controls display of picture-in-picture
'''
class Pip(object):

    # constructor
    def __init__(self, imagefilename):

        self.imagefilename = imagefilename
        self.imagefile = u"/dev/shm/" + imagefilename
        self.settingsValid = False
        self.uuidfile = None

        self.settings = {}
        self.imgHdl = None
        self.img = False
        self.lblNbrHdl = None
        self.lblNameHdl = None
        self.channelnumber = 1
        self.channelname = u""

        self.x = 20
        self.y = 110
        self.w = 320
        self.h = 260

        self.winId = 15005
        self.winHdl = xbmcgui.Window(self.winId)


    # get addon settings
    def get_settings(self, addon):

        # get addon settings and convert them to a dictionary
        if addon.getSetting(u'top') == u'true':
            self.settings[u'top'] = True
        else:
            self.settings[u'top'] = False

        if addon.getSetting(u'left') == u'true':
            self.settings[u'left'] = True
        else:
            self.settings[u'left'] = False

        self.settings[u'xgap'] = int(addon.getSetting(u'xgap'))
        self.settings[u'ygap'] = int(addon.getSetting(u'ygap'))
        self.settings[u'width'] = int(addon.getSetting(u'width'))
        self.settings[u'height'] = int(addon.getSetting(u'height'))
        self.settings[u'fps'] = int(addon.getSetting(u'fps'))
        self.settings[u'ipaddress'] = unicode(addon.getSetting(u'ipaddress'))
        self.settings[u'port'] = unicode(addon.getSetting(u'port'))
        self.settings[u'username'] = unicode(addon.getSetting(u'username'))
        self.settings[u'password'] = unicode(addon.getSetting(u'password'))
        self.settings[u'profile'] = unicode(addon.getSetting(u'profile'))
        self.settings[u'tmpfolder'] = unicode(addon.getSetting(u'tmpfolder'))
        self.settings[u'ffmpegopts'] = unicode(addon.getSetting(u'ffmpegopts'))
        self.settings[u'keytoggle'] = unicode(addon.getSetting(u'keytoggle'))
        self.settings[u'keyback'] = unicode(addon.getSetting(u'keyback'))
        self.settings[u'keyup'] = unicode(addon.getSetting(u'keyup'))
        self.settings[u'keydown'] = unicode(addon.getSetting(u'keydown'))

        self.settingsValid = False
        if self.settings[u'tmpfolder'].replace(u" ", u"") == u"":

            if platform.system() == u"Linux":
                xbmc.log(u"[pip-service] Detected Linux platform", xbmc.LOGDEBUG)
                # test if /dev/shm is available and accessible
                tmpfolder = u"/dev/shm"
                try:
                    fobj = open(tmpfolder + u"/writetest.txt", u"w")
                    fobj.close()
                    self.settings[u'tmpfolder'] = u"/dev/shm"
                    self.settingsValid = True
                except IOError:
                    xbmc.log(u"[pip-service] Folder '%s' is not usable on detected Linux platform. Please define a ramdisk folder manually via addon configuration." % tmpfolder, xbmc.LOGERROR)
                    self.settingsValid = False

            if platform.system() == u"Windows":
                xbmc.log(u"[pip-service] Detected Windows platform", xbmc.LOGDEBUG)
                xbmc.log(u"[pip-service] Windows platform does not provide a standard ramdisk. Please create a ramdisk and define the path to it manually via addon configuration." % tmpfolder, xbmc.LOGERROR)
                self.settingsValid = False

        self.imagefile = u"%s/%s" % (self.settings[u'tmpfolder'], self.imagefilename)

        # return settings as dictionary
        return self.settings


    # return status of parsed settings
    def get_settings_status(self):
        return self.settingsValid


    # initial image control
    def init_image(self):

        # get current windows ID
        winId = xbmcgui.getCurrentWindowId()

        # copy or overwrite keymap xml
        wait4pipimage = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo(u'path')) + u"/resources/data/wait4pip.png"
        shutil.copy(wait4pipimage, self.imagefile)

        # if video fullscreen window ID
        if winId == self.winId and os.path.exists(self.imagefile):

            # remove control before new creation
            if self.img:
                self.winHdl.removeControl(self.imgHdl)
                del self.imgHdl
                self.winHdl.removeControl(self.lblNbrHdl)
                del self.lblNbrHdl
                self.winHdl.removeControl(self.lblNameHdl)
                del self.lblNameHdl
                self.img = False

            # define dimensions
            wwin = self.winHdl.getWidth()
            hwin = self.winHdl.getHeight()
            xbmc.log(u"[pip-service] windows size: %d x %d" % (wwin, hwin), xbmc.LOGINFO)
            self.w = self.settings[u'width']
            self.h = self.settings[u'height']
            if self.settings[u'left']:
                self.x = self.settings[u'xgap']
            else:
                self.x = wwin - self.settings[u'xgap'] - self.w
            if self.settings[u'top']:
                self.y = self.settings[u'ygap']
            else:
                self.y = hwin - self.settings[u'ygap'] - self.h
            xbmc.log(u"[pip-service] x and y: %d x %d" % (self.x, self.y), xbmc.LOGINFO)

            # create image control
            self.imgHdl = xbmcgui.ControlImage(self.x, self.y, self.w, self.h, self.imagefile)
            self.imgHdl.setAnimations([(u'visible', u'effect=fade end=100 time=300 delay=300',)])

            # add image control to windows handle
            self.winHdl.addControl(self.imgHdl)

            # add channel number label control to windows handle
            self.lblNbrHdl = xbmcgui.ControlLabel(self.x + 5, self.y, self.x + self.w - 40, 125, u"%s" % (self.channelnumber))
            self.winHdl.addControl(self.lblNbrHdl)

            # add channel number label control to windows handle
            self.lblNameHdl = xbmcgui.ControlLabel(self.x + 5, self.y + self.h, self.x + self.w - 40, 125, u"%s" % (self.channelname), font=u'font10')
            self.winHdl.addControl(self.lblNameHdl)

            self.img = True


    # display picture-in-picture image if avaiable
    def show_image(self, waitimg):

        # get current windows ID
        winId = xbmcgui.getCurrentWindowId()

        if waitimg:
            # copy or overwrite keymap xml
            wait4pipimage = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo(u'path')) + u"/resources/data/wait4pip.png"
            shutil.copy(wait4pipimage, self.imagefile)

        # if video fullscreen window ID
        if winId == self.winId and os.path.exists(self.imagefile):

            # set channel number label text
            self.lblNbrHdl.setLabel(u"%s" % (self.channelnumber))

            # set channel number label text
            self.lblNameHdl.setLabel(u"%s" % (self.channelname))

            # add to latest captured image a unique id in order to force reload the image via setImage function
            olduuidfile = self.uuidfile
            self.uuidfile = self.imagefile.replace(u".png", u"%s.png" % unicode(uuid.uuid4()))
            try:
                # copy thumb.png to thumb[uuid].png
                shutil.copy(self.imagefile, self.uuidfile)

                # set new image file
                self.imgHdl.setImage(self.uuidfile, useCache = False)
            except FileNotFoundError:
                pass

            # remove already set image file if it exists
            if olduuidfile != None:
                if os.path.exists(olduuidfile):
                    os.remove(olduuidfile)


    # hide image by removeing controls
    def hide_image(self):
        if self.img:
            self.winHdl.removeControl(self.imgHdl)
            del self.imgHdl
            self.winHdl.removeControl(self.lblNbrHdl)
            del self.lblNbrHdl
            self.winHdl.removeControl(self.lblNameHdl)
            del self.lblNameHdl
            self.img = False


    # set channel number
    def set_channel(self, name, number):
        self.channelname = name
        self.channelnumber = unicode(number)
