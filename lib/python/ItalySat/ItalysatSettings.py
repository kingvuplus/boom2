# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatSettings.py
from Screens.Screen import Screen
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.InputBox import InputBox
from Screens.Setup import Setup
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigNumber, ConfigSelection, ConfigClock, NoSave, configfile
from Components.Sources.List import List
from Components.Console import Console
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, createDir, resolveFilename, SCOPE_SKIN_IMAGE
from os import system, statvfs, remove as os_remove, rename as os_rename, stat as mystat, popen, getcwd, chdir, listdir
import stat
from boxbranding import getMachineBrand, getMachineName, getBoxType
from ItalysatUtils import ItalysatGetSkinPath
import time
import datetime

class ItalysatSettings(Screen):
    skin = '\n\t<screen name="ItalySettings" position="center,center" size="572,454" title="ItalySat Settings">\n\t  <widget source="list" render="Listbox" position="12,10" size="549,438" scrollbarMode="showOnDemand">\n\t    <convert type="TemplatedMultiContent">\n\t                \t\t{"template": [\n\t                \t\tMultiContentEntryText(pos = (60, 1), size = (300, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n\t                \t\tMultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 1),\n\t                \t\t],\n\t                \t\t"fonts": [gFont("Regular", 24)],\n\t                \t\t"itemHeight": 36\n\t                \t\t}\n\t            \t\t</convert>\n\t  </widget>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self.updateList()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'back': self.close})

    def KeyOk(self):
        self.sel = self['list'].getCurrent()
        self.sel = self.sel[2]
        if self.sel == 0:
            from ItalysatRam import ItalyRamPanel
            self.session.open(ItalyRamPanel)
        elif self.sel == 1:
            from ItalysatDevice import ItalyDevicesPanel
            self.session.open(ItalyDevicesPanel)
        elif self.sel == 2:
            from ItalysatKernelDownload import ItalyKernelModule
            self.session.open(ItalyKernelModule)
        elif self.sel == 3:
            from ItalysatNetwork import ItalyNetworkList
            self.session.open(ItalyNetworkList)
        elif self.sel == 4:
            from ItalysatSwapManager import ItalySwapPanel
            self.session.open(ItalySwapPanel)
        elif self.sel == 5:
            from ItalysatCronManager import ItalyCronManager
            self.session.open(ItalyCronManager)
        elif self.sel == 6:
            self.session.open(ItalyFastPlugin)
        elif self.sel == 7:
            self.session.open(ItalyPcsc)
        elif self.sel == 8:
            from ItalysatDttDownload import ItalyDttModule
            self.session.open(ItalyDttModule)
        elif self.sel == 9:
            from ItalysatWifiDownload import ItalyWifiModule
            self.session.open(ItalyWifiModule)
        else:
            self.noYet()

    def noYet(self):
        nobox = self.session.open(MessageBox, _('Selected Function is Not Available'), MessageBox.TYPE_INFO)
        nobox.setTitle(_('Info'))

    def updateList(self):
        self.list = []
        mypath = ItalysatGetSkinPath()
        mypixmap = mypath + 'italy_icons/settings_ram.png'
        png = LoadPixmap(mypixmap)
        name = _('Memory RAM Manager')
        idx = 0
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_device.png'
        png = LoadPixmap(mypixmap)
        name = _('Device Manager')
        idx = 1
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_djmount.png'
        png = LoadPixmap(mypixmap)
        name = _('Kernel Module')
        idx = 2
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_djmount.png'
        png = LoadPixmap(mypixmap)
        name = _('Network Manager')
        idx = 3
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_swap.png'
        png = LoadPixmap(mypixmap)
        name = _('Swap Manager')
        idx = 4
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_contrab.png'
        png = LoadPixmap(mypixmap)
        name = _('Cron Manager')
        idx = 5
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_fastplugin.png'
        png = LoadPixmap(mypixmap)
        name = _('Fast Plugin Manager')
        idx = 6
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_pcsc.png'
        png = LoadPixmap(mypixmap)
        name = _('Pcsc Manager')
        idx = 7
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_dtt.png'
        png = LoadPixmap(mypixmap)
        name = _('DVB-T Manager')
        idx = 8
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_dtt.png'
        png = LoadPixmap(mypixmap)
        name = _('Wifi Manager')
        idx = 9
        res = (name, png, idx)
        self.list.append(res)
        self['list'].list = self.list

    def myclose(self):
        self.close()


class ItalyFastPlugin(Screen):
    skin = '\n\t<screen name="Italy Fast Plugin Setup" position="center,center" size="517,487">\n\t\t<widget source="list" render="Listbox" position="10,10" size="494,403" scrollbarMode="showOnDemand">\n\t\t\t<convert type="StringList" />\n\t\t</widget>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="197,433" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="198,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Label(_('Set Favourite'))
        self.list = []
        self['list'] = List(self.list)
        self.updateList2()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.save,
         'back': self.close,
         'red': self.save}, -1)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('ItalySat Fast Plugin Manager'))

    def updateList2(self):
        self.list = []
        self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
        for plugin in self.pluginlist:
            if plugin.icon is None:
                png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/icons/plugin.png'))
            else:
                png = plugin.icon
            res = (plugin.name, plugin.description, png)
            self.list.append(res)

        self['list'].list = self.list
        return

    def save(self):
        mysel = self['list'].getCurrent()
        if mysel:
            mysel = mysel[0]
            message = _('Fast plugin set to: ') + mysel + _('\nKey: 2x Green')
            mybox = self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO)
            mybox.setTitle(_('Configuration Saved'))
            config.italysat.fp.value = mysel
            config.italysat.fp.save()
            configfile.save()


class ItalyPcsc(Screen):
    skin = '\n\t<screen position="center,center" size="602,305">\n\t\t<widget name="lab1" position="20,30" size="580,60" font="Regular;20" valign="center" transparent="1"/>\n\t\t<widget name="lab2" position="20,150" size="300,30" font="Regular;20" valign="center" transparent="1"/>\n\t\t<widget name="labstop" position="320,150" size="150,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>\n\t\t<widget name="labrun" position="320,150" size="150,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="125,260" size="150,30" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="325,260" size="150,30" alphatest="on"/>\n\t\t<widget name="key_red" position="125,262" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>\n\t\t<widget name="key_green" position="325,262" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Pcsc service for Usb readers.'))
        self['lab2'] = Label(_('Current Status:'))
        self['labstop'] = Label(_('Stopped'))
        self['labrun'] = Label(_('Running'))
        self['key_red'] = Label('Enable')
        self['key_green'] = Label('Disable')
        self.my_serv_active = False
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.UninstallCheck,
         'red': self.ServStart,
         'green': self.ServStop})
        self.Console = Console()
        self.service_name = 'pcsc-lite pcsc-lite-lib'
        self.InstallCheck()
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('ItalySat Pcsc Manager'))

    def InstallCheck(self):
        self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

    def checkNetworkState(self, str, retval, extra_args):
        if not str:
            self.feedscheck = self.session.open(MessageBox, _('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input=False)
            self.feedscheck.setTitle(_('Checking Feeds'))
            cmd1 = 'opkg update'
            self.CheckConsole = Console()
            self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)
        else:
            self.updateServ()

    def checkNetworkStateFinished(self, result, retval, extra_args = None):
        if result.find('No space left on device') != -1:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _('Your %s %s have a FULL flash memory, please free memory or expand in USB') % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        elif result.find('bad address') != -1:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _('Your %s %s is not connected to the internet, please check your network settings and try again.') % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        elif result.find('wget returned 1') != -1 or result.find('wget returned 255') != -1 or result.find('404 Not Found') != -1:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _('Sorry feeds are down for maintenance, please try again later.'), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        else:
            self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install "%s" ?') % self.service_name, MessageBox.TYPE_YESNO)

    def InstallPackage(self, val):
        if val:
            self.doInstall(self.installComplete, self.service_name)
        else:
            self.feedscheck.close()
            self.close()

    def InstallPackageFailed(self, val):
        self.feedscheck.close()
        self.close()

    def doInstall(self, callback, pkgname):
        self.message = self.session.open(MessageBox, _('please wait...'), MessageBox.TYPE_INFO, enable_input=False)
        self.message.setTitle(_('Installing Service'))
        self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

    def installComplete(self, result = None, retval = None, extra_args = None):
        self.message.close()
        self.feedscheck.close()
        self.updateServ()

    def UninstallCheck(self):
        if self.my_serv_active == False:
            self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.RemovedataAvail)
        else:
            self.close()

    def RemovedataAvail(self, str, retval, extra_args):
        if str:
            self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove "%s" ?') % self.service_name)
        else:
            self.close()

    def RemovePackage(self, val):
        if val:
            self.doRemove(self.removeComplete, self.service_name)
        else:
            self.close()

    def doRemove(self, callback, pkgname):
        self.message = self.session.open(MessageBox, _('please wait...'), MessageBox.TYPE_INFO, enable_input=False)
        self.message.setTitle(_('Removing Service'))
        self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-removal-of-dependent-packages', callback)

    def removeComplete(self, result = None, retval = None, extra_args = None):
        self.message.close()
        self.close()

    def ServStart(self):
        if self.my_serv_active == False:
            rc = system('ln -s /etc/init.d/pcscd /etc/rc3.d/S20pcscd')
            rc = system('/etc/init.d/pcscd start')
            mybox = self.session.open(MessageBox, _('Pcsc Enabled.'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
            self.updateServ()

    def ServStop(self):
        if self.my_serv_active == True:
            rc = system('/etc/init.d/pcscd stop')
            if fileExists('/etc/rc3.d/S20pcscd'):
                os_remove('/etc/rc3.d/S20pcscd')
            mybox = self.session.open(MessageBox, _('Pcsc Client Disabled.'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
            rc = system('sleep 1')
            self.updateServ()

    def updateServ(self):
        self['labrun'].hide()
        self['labstop'].hide()
        rc = system('ps x > /tmp/.ps.tmp')
        self.my_serv_active = False
        if fileExists('/tmp/.ps.tmp'):
            f = open('/tmp/.ps.tmp', 'r')
            for line in f.readlines():
                if line.find('pcscd') != -1:
                    self.my_serv_active = True

            f.close()
            os_remove('/tmp/.ps.tmp')
        if self.my_serv_active == True:
            self['labstop'].hide()
            self['labrun'].show()
        else:
            self['labstop'].show()
            self['labrun'].hide()