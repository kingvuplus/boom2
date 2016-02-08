# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatKernelDownload.py
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from os import system, popen
from ItalysatUtils import ItalysatGetSkinPath
from boxbranding import getMachineBrand, getMachineName

class ItalyKernelModule(Screen):
    __module__ = __name__
    skin = '\n\t<screen position="center,center" size="634,474">\n\t\t\t<widget source="list" render="Listbox" position="12,6" size="611,424" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=3),\n\t\t\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t    <ePixmap pixmap="skin_default/buttons/red.png" position="158,434" size="140,40" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/green.png" position="369,433" size="140,40" alphatest="on" />\n\t\t    <widget name="key_red" position="157,434" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    <widget name="key_green" position="367,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.modules = [('ftdi_sio',
          _('Smargo & other Usb card readers chipset ftdi'),
          'kernel-module-ftdi-sio',
          True), ('pl2303',
          _('Other Usb card readers chipset pl2303'),
          'kernel-module-pl2303',
          True), ('tun',
          _('Tun module needed for Openvpn'),
          'kernel-module-tun',
          True)]
        self.modstatus = {}
        self.list = []
        self['key_red'] = Label(_('Remove'))
        self['key_green'] = Label(_('Restart E2'))
        self['list'] = List(self.list)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.UninstallCheck,
         'green': self.runFinishedRe2,
         'back': self.close})
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.updateList)
        self.Console = Console()

    def setWindowTitle(self):
        self.setTitle(_('Manage Modules'))

    def KeyOk(self):
        sel = self['list'].getCurrent()[2]
        if sel:
            self.Console.ePopen('/usr/bin/opkg list_installed ' + sel, self.checkNetworkState)

    def executedScript(self, *answer):
        self.updateList()

    def readStatus(self):
        for mod in self.modules:
            self.modstatus[mod[0]] = False

        system('lsmod > /tmp/status.log')
        try:
            f = open('/tmp/status.log', 'r')
            for line in f.readlines():
                for mod in self.modules:
                    if line.find(mod[0]) != -1:
                        self.modstatus[mod[0]] = True

            f.close()
        except:
            pass

    def updateList(self):
        self.readStatus()
        del self.list[:]
        skin_path = ItalysatGetSkinPath()
        for mod in self.modules:
            if mod[3]:
                png = LoadPixmap({True: skin_path + 'italy_icons/menu_on.png',
                 False: skin_path + 'italy_icons/menu_off.png'}[self.modstatus.get(mod[0])])
                self.list.append((mod[0],
                 mod[1],
                 mod[2],
                 png))

        self['list'].setList(self.list)

    def checkNetworkState(self, str, retval, extra_args):
        if not str:
            self.feedscheck = self.session.open(MessageBox, _('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input=False)
            self.feedscheck.setTitle(_('Checking Feeds'))
            cmd1 = 'opkg update'
            self.CheckConsole = Console()
            self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)
        else:
            self.feedscheck = self.session.open(MessageBox, _('Module is already installed'), MessageBox.TYPE_INFO, timeout=5, close_on_any_key=True)
            self.feedscheck.setTitle(_('Message'))
            sel = self['list'].getCurrent()[0]
            if sel:
                system('modprobe -v ' + sel)
            self.updateList()

    def checkNetworkStateFinished(self, result, retval, extra_args = None):
        sel = self['list'].getCurrent()[2]
        if result.find('No space left on device') != -1:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _('Your %s %s have a FULL flash memory, please free memory or expand in USB') % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        elif result.find('bad address') != -1:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _('Your %s %s is not connected to the internet, please check your network settings and try again.') % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        elif result.find('wget returned 1') != -1 or result.find('wget returned 255') != -1 or result.find('404 Not Found') != -1:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _('Sorry feeds are down for maintenance, please try again later.'), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        else:
            self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install "%s" ?') % sel, MessageBox.TYPE_YESNO)

    def InstallPackage(self, val):
        sel = self['list'].getCurrent()[2]
        if val:
            self.doInstall(self.installComplete, sel)
        else:
            self.feedscheck.close()
            self.updateList()

    def InstallPackageFailed(self, val):
        self.feedscheck.close()
        self.updateList()

    def doInstall(self, callback, pkgname):
        self.message = self.session.open(MessageBox, _('please wait...'), MessageBox.TYPE_INFO, enable_input=False)
        self.message.setTitle(_('Installing Service'))
        self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

    def installComplete(self, result = None, retval = None, extra_args = None):
        sel = self['list'].getCurrent()[0]
        if sel:
            system('modprobe -v ' + sel)
        self.message.close()
        self.feedscheck.close()
        self.updateList()

    def UninstallCheck(self):
        sel = self['list'].getCurrent()[2]
        self.Console.ePopen('/usr/bin/opkg list_installed ' + sel, self.RemovedataAvail)

    def RemovedataAvail(self, str, retval, extra_args):
        sel = self['list'].getCurrent()[2]
        if str:
            self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove "%s" ?') % sel)
        else:
            self.updateList()

    def RemovePackage(self, val):
        sel = self['list'].getCurrent()[2]
        if val:
            self.doRemove(self.removeComplete, sel)
        else:
            self.updateList()

    def doRemove(self, callback, pkgname):
        self.message = self.session.open(MessageBox, _('please wait...'), MessageBox.TYPE_INFO, enable_input=False)
        self.message.setTitle(_('Removing Service'))
        self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-remove --autoremove', callback)

    def removeComplete(self, result = None, retval = None, extra_args = None):
        sel = self['list'].getCurrent()[0]
        if sel:
            system('modprobe -rv ' + sel)
        self.message.close()
        self.updateList()

    def runFinishedRe2(self):
        msg = _('Enigma2 will be now hard restarted to activate module.\nDo You want restart enigma2 now?')
        box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('Restart enigma'))

    def restartEnigma2(self, answer):
        if answer is True:
            system('killall -9 enigma2')