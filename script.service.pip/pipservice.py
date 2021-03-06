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

from __future__ import division
from __future__ import absolute_import
import xbmc
import xbmcaddon



from resources.lib.m3u import M3u
from resources.lib.ffmpeg import Ffmpeg
from resources.lib.pip import Pip
from resources.lib.keymap import Keymap


# addon infos
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo(u'name')
__icon__ = __addon__.getAddonInfo(u'icon')


# files
imagefilename = "thumb.png"


u'''
Class XbmcMonitor
xbmc monitor with on notification and on settings changed handler
'''
class XbmcMonitor( xbmc.Monitor ):

    # constructor
    def __init__(self):
        self.toggled = False
        self.channelup = False
        self.channeldown = False
        self.channelback = False
        self.changed = False


    # get toggle status
    def get_toggle_status(self):
        ret = self.toggled
        self.toggled = False
        return ret


    # get channel up status
    def get_channel_up_status(self):
        ret = self.channelup
        self.channelup = False
        return ret


    # get channel down status
    def get_channel_down_status(self):
        ret = self.channeldown
        self.channeldown = False
        return ret


    # get channel back status
    def get_channel_back_status(self):
        ret = self.channelback
        self.channelback = False
        return ret


    # called on a notification
    def onNotification(self, sender, method, data):

        if sender == u"service.pip":
            xbmc.log(u"[pip-service] key press detected!", xbmc.LOGINFO)
            if method == u"Other.toggle_pip":
                xbmc.log(u"[pip-service] via notifiyAll: sender=%s, method=%s, data=%s" % (unicode(sender), unicode(method), unicode(data)), xbmc.LOGDEBUG)
                self.toggled= True

            if method == u"Other.channel_up_pip":
                xbmc.log(u"[pip-service] via notifiyAll: sender=%s, method=%s, data=%s" % (unicode(sender), unicode(method), unicode(data)), xbmc.LOGDEBUG)
                self.channelup = True

            if method == u"Other.channel_down_pip":
                xbmc.log(u"[pip-service] via notifiyAll: sender=%s, method=%s, data=%s" % (unicode(sender), unicode(method), unicode(data)), xbmc.LOGDEBUG)
                self.channeldown= True

            if method == u"Other.channel_back_pip":
                xbmc.log(u"[pip-service] via notifiyAll: sender=%s, method=%s, data=%s" % (unicode(sender), unicode(method), unicode(data)), xbmc.LOGINFO)
                self.channelback= True


    # get settings changed status
    def get_settings_changed_status(self):
        changed = self.changed
        self.changed = False
        return changed


    # called on settings changed
    def onSettingsChanged(self):
        xbmc.log(u"[pip-service] settings have changed.", xbmc.LOGINFO)
        self.changed = True



u'''
Main function
'''
if __name__ == u'__main__':

    upDownTimer = 0

    # init pip
    xbmc.log(u'[pip-service] Starting', xbmc.LOGINFO)
    pip = Pip(imagefilename)

    # get settings
    settings = pip.get_settings(__addon__)
    pip.init_image()
    pip.show_image(True)

    # init keymap
    keymap = Keymap(xbmc.translatePath(u"special://userdata/keymaps/"))
    keymap.update(settings[u'keytoggle'], settings[u'keyback'], settings[u'keyup'], settings[u'keydown'])
    keymap.create()

    # init m3u
    m3u = M3u(settings[u'username'],
              settings[u'password'],
              settings[u'ipaddress'],
              settings[u'port'],
              settings[u'profile'])

    # download and parse channels
    m3u.download()
    m3u.parse()

    # get all available channel ids
    m3u.get_channel_ids()

    # start a xbmc monitor
    monitor = XbmcMonitor()

    # init ffmpeg
    ffmpeg = Ffmpeg(imagefilename,
                    settings[u'tmpfolder'],
                    settings[u'username'],
                    settings[u'password'],
                    settings[u'fps'],
                    settings[u'ffmpegopts'],
                    settings[u'width'])

    # test if ffmpeg executable is available
    if ffmpeg.test() and pip.get_settings_status():
        xbmc.log(u'[pip-service] ffmpeg.test()', xbmc.LOGINFO)
        # loop until monitor reports an abort
        sleeptime = float(1/settings[u'fps'])
        while not monitor.waitForAbort(sleeptime):
            xbmc.log(u'[pip-service] while not monitor.', xbmc.LOGINFO)
            if monitor.get_settings_changed_status():
                xbmc.log(u'[pip-service] get_settings_changed_status.', xbmc.LOGINFO)
                # update pip settings
                settings = pip.get_settings(__addon__)
                if pip.get_settings_status() == False:
                    break

                # update keymap
                keymap.update(settings[u'keytoggle'], settings[u'keyback'], settings[u'keyup'], settings[u'keydown'])
                keymap.create()

                # update m3u settings
                m3u.update_settings(settings[u'username'],
                                    settings[u'password'],
                                    settings[u'ipaddress'],
                                    settings[u'port'],
                                    settings[u'profile'])

                # download and parse channels
                m3u.download()
                m3u.parse()

                # reinit image control
                pip.init_image()

                # update ffmpeg settings
                ffmpeg.update_settings( settings[u'tmpfolder'],
                                        settings[u'username'],
                                        settings[u'password'],
                                        settings[u'fps'],
                                        settings[u'ffmpegopts'],
                                        settings[u'width'])


            if monitor.get_toggle_status():
                if ffmpeg.started():
                    # stop picture in picture capturing
                    ffmpeg.stop()
                    xbmc.log(u"[pip-service] stopped ffmpeg process.", xbmc.LOGDEBUG)

                else:
                    # start picture in picture capturing using ffmpeg
                    url, channelname = m3u.get_url()
                    channelnumber = m3u.channel2number[channelname]
                    pip.set_channel(channelname, channelnumber)

                    if url == u"":
                        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"No URL found ...", 2000, __icon__))
                        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"Not started ...", 2000, __icon__))
                    else:
                        pip.init_image()
                        ffmpeg.start(url, False)
                        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"Starting ...", 5000, __icon__))
                        xbmc.log(u"[pip-service] started ffmpeg process.", xbmc.LOGDEBUG)


            if monitor.get_channel_back_status():
                # switch back to pip channel
                channelname = m3u.get_channel_name()
                m3u.switch_channel(channelname)

                # stop picture in picture capturing
                ffmpeg.stop()
                xbmc.log(u"[pip-service] stopped ffmpeg process.", xbmc.LOGDEBUG)


            if monitor.get_channel_up_status():
                upDownTimer = int(100 / settings[u'fps'])

                # switch one channel up of pip channel
                channelname = m3u.get_channel_name()
                channelnumber = m3u.channel2number[channelname]

                if (channelnumber + 1) in m3u.number2url:
                    url = m3u.number2url[channelnumber + 1]

                    # set new channel name depending on increased channel number
                    m3u.set_channel_name(channelnumber + 1)

                    # restart picture in picture capturing
                    ffmpeg.stop()

                    # "wait" image
                    pip.set_channel(m3u.get_channel_name(), channelnumber + 1)
                    pip.show_image(True)



            if monitor.get_channel_down_status():
                upDownTimer = int(100 / settings[u'fps'])

                # switch one channel down of pip channel
                channelname = m3u.get_channel_name()
                channelnumber = m3u.channel2number[channelname]

                if (channelnumber - 1) in m3u.number2url:
                    url = m3u.number2url[channelnumber - 1]

                    # set new channel name depending on decreased channel number
                    m3u.set_channel_name(channelnumber - 1)

                    # restart picture in picture capturing
                    ffmpeg.stop()

                    # "wait" image
                    pip.set_channel(m3u.get_channel_name(), channelnumber - 1)
                    pip.show_image(True)


            # decrease channel up/down timer and limit it to 0
            upDownTimer = upDownTimer - 1
            if upDownTimer <= 0:
                upDownTimer = 0
            else:
                xbmc.log(u"[pip-service] updown timer %d." % upDownTimer, xbmc.LOGINFO)


            # if up/down timer has reached "1" start ffmpeg with latest requested url
            if upDownTimer == 1:
                # start start
                ffmpeg.start(url, False)
                xbmc.log(u"[pip-service] FFMPEOG starte. %s " % url, xbmc.LOGINFO)


            if ffmpeg.started() and not ffmpeg.running():
                # restart ffmpeg
                ffmpeg.start(url, True)
                xbmc.log(u"[pip-service] re-started ffmpeg process for %s." % url, xbmc.LOGWARNING)


            if ffmpeg.started():
                # display picture-in-picture if a capture image from ffmpeg process is available
                pip.show_image(False)
            elif upDownTimer <= 0:
                pip.hide_image()

        # stop ffmpeg process if running
        ffmpeg.stop()


    # report some error infos to user
    if not ffmpeg.test():
        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"No ffmpeg executable found ...", 2000, __icon__))
        xbmc.log(u"[pip-service] no ffmpeg executable available!", xbmc.LOGERROR)

    if not pip.get_settings_status():
        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"Create a ramdisk and use it as temporary folder in the addon configuration.", 2000, __icon__))
        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"Using a temporary folder on a ramdisk is highly recommended ", 2000, __icon__))
        xbmc.executebuiltin(u'Notification(%s, %s, %d, %s)'%(__addonname__, u"to avoid too many write accesses to the harddisc!", 2000, __icon__))


    # clean up before exit
    del ffmpeg
    del m3u
    del monitor
    del pip
    del __addon__

    xbmc.log(u'[pip-service] finished, exiting', xbmc.LOGINFO)
