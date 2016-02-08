# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatNetwork.py
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from os import system, remove as os_remove, popen
import stat
import time
from enigma import eEnv
from boxbranding import getMachineBrand, getMachineName
from ItalysatUtils import ItalysatGetSkinPath
plugin_path_networkbrowser = eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/NetworkBrowser')

class ItalyNetworkList(Screen):
    skin = '\n\t<screen name="ItalyNetworkList" position="center,center" size="572,454" title="ItalySat Network List">\n\t  <widget source="list" render="Listbox" position="12,10" size="549,438" scrollbarMode="showOnDemand">\n\t    <convert type="TemplatedMultiContent">\n\t                \t\t{"template": [\n\t                \t\tMultiContentEntryText(pos = (60, 1), size = (300, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n\t                \t\tMultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 1),\n\t                \t\t],\n\t                \t\t"fonts": [gFont("Regular", 24)],\n\t                \t\t"itemHeight": 36\n\t                \t\t}\n\t            \t\t</convert>\n\t  </widget>\n\t</screen>'

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
            from Screens.NetworkSetup import NetworkOpenvpn
            self.session.open(NetworkOpenvpn)
        elif self.sel == 1:
            from Screens.NetworkSetup import NetworkInadyn
            self.session.open(NetworkInadyn)
        elif self.sel == 2:
            from Screens.NetworkSetup import NetworkSamba
            self.session.open(NetworkSamba)
        elif self.sel == 3:
            from Screens.NetworkSetup import NetworkTelnet
            self.session.open(NetworkTelnet)
        elif self.sel == 4:
            from Screens.NetworkSetup import NetworkFtp
            self.session.open(NetworkFtp)
        elif self.sel == 5:
            from Screens.NetworkSetup import NetworkNfs
            self.session.open(NetworkNfs)
        elif self.sel == 6:
            from Screens.NetworkSetup import NetworkuShare
            self.session.open(NetworkuShare)
        elif self.sel == 7:
            self.session.open(ItalyMediatombPanel)
        elif self.sel == 8:
            from Screens.NetworkSetup import NetworkMiniDLNA
            self.session.open(NetworkMiniDLNA)
        elif self.sel == 9:
            from Screens.NetworkSetup import NetworkAfp
            self.session.open(NetworkAfp)
        elif self.sel == 10:
            from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
            self.session.open(NetworkBrowser, None, plugin_path_networkbrowser)
        else:
            self.noYet()
        return

    def noYet(self):
        nobox = self.session.open(MessageBox, _('Selected Function is Not Available'), MessageBox.TYPE_INFO)
        nobox.setTitle(_('Info'))

    def updateList(self):
        self.list = []
        mypath = ItalysatGetSkinPath()
        mypixmap = mypath + 'italy_icons/settings_vpn.png'
        png = LoadPixmap(mypixmap)
        name = _('OpenVpn Manager')
        idx = 0
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_inadyn.png'
        png = LoadPixmap(mypixmap)
        name = _('InaDyn Manager')
        idx = 1
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_samba.png'
        png = LoadPixmap(mypixmap)
        name = _('Samba/Cifs Manager')
        idx = 2
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_telnet.png'
        png = LoadPixmap(mypixmap)
        name = _('Telnet Manager')
        idx = 3
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_ftp.png'
        png = LoadPixmap(mypixmap)
        name = _('Ftp Manager')
        idx = 4
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_nfs.png'
        png = LoadPixmap(mypixmap)
        name = _('Nfs Server Manager')
        idx = 5
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_djmount.png'
        png = LoadPixmap(mypixmap)
        name = _('uShare Manager')
        idx = 6
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_mediatomb.png'
        png = LoadPixmap(mypixmap)
        name = _('UPnP Server Mediatomb Manager')
        idx = 7
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_minidlna.png'
        png = LoadPixmap(mypixmap)
        name = _('Mini DLNa Manager')
        idx = 8
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_minidlna.png'
        png = LoadPixmap(mypixmap)
        name = _('Apple AFP Manager')
        idx = 9
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/settings_nfs.png'
        png = LoadPixmap(mypixmap)
        name = _('Network Mount Manager')
        idx = 10
        res = (name, png, idx)
        self.list.append(res)
        self['list'].list = self.list


class ItalyMediatombPanel(Screen):
    skin = '\n\t<screen position="center,center" size="602,405">\n\t\t<widget name="lab1" position="20,20" size="580,260" font="Regular;20" valign="center" transparent="1"/>\n\t\t<widget name="lab2" position="20,300" size="300,30" font="Regular;20" valign="center" transparent="1"/>\n\t\t<widget name="labstop" position="320,300" size="150,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>\n\t\t<widget name="labstart" position="320,300" size="150,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="125,360" size="150,30" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="325,360" size="150,30" alphatest="on"/>\n\t\t<widget name="key_red" position="125,362" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>\n\t\t<widget name="key_green" position="325,362" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        mytext = _('Mediatomb: UPnP media server.\nMediatomb is fully configured for your box and ready to work. Just enable it and play.\nMediatomb include a nice web interface url to manage your media.\n\nMediatomb webif url: http://ip_box:49152\nMediatomb configs: /.mediatomb/config.xml\nMediatomb docs & howto: http://mediatomb.cc/')
        self['lab1'] = Label(mytext)
        self['lab2'] = Label(_('Current Status:'))
        self['labstop'] = Label(_('Stopped'))
        self['labstart'] = Label(_('Running'))
        self['key_red'] = Label(_('Enable'))
        self['key_green'] = Label(_('Disable'))
        self.my_serv_active = False
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.UninstallCheck,
         'red': self.ServStart,
         'green': self.ServStop})
        self.Console = Console()
        self.service_name = 'enigma2-plugin-extensions-mediatomb'
        self.InstallCheck()
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('ItalySat Mediatomb Manager'))

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
        self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-remove --autoremove', callback)

    def removeComplete(self, result = None, retval = None, extra_args = None):
        self.message.close()
        self.close()

    def ServStart(self):
        if self.my_serv_active == False:
            rc = system('ln -s ../init.d/mediatomb /etc/rc3.d/S20mediatomb')
            rc = system('/etc/init.d/mediatomb start')
            mybox = self.session.open(MessageBox, _('UPnP Server Enabled.'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
            self.updateServ()

    def ServStop(self):
        if self.my_serv_active == True:
            rc = system('/etc/init.d/mediatomb stop')
            if fileExists('/etc/rc3.d/S20mediatomb'):
                os_remove('/etc/rc3.d/S20mediatomb')
            mybox = self.session.open(MessageBox, _('UPnP Server Disabled.'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
            rc = system('sleep 1')
            self.updateServ()

    def updateServ(self):
        self['labstart'].hide()
        self['labstop'].hide()
        rc = system('ps x > /tmp/.ps.tmp')
        self.my_serv_active = False
        if fileExists('/tmp/.ps.tmp'):
            f = open('/tmp/.ps.tmp', 'r')
            for line in f.readlines():
                if line.find('mediatomb') != -1:
                    self.my_serv_active = True

            f.close()
            os_remove('/tmp/.ps.tmp')
        if self.my_serv_active == True:
            self['labstop'].hide()
            self['labstart'].show()
        else:
            self['labstop'].show()
            self['labstart'].hide()