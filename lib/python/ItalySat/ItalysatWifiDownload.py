# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatWifiDownload.py
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console as x_Console
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from os import system, popen
from boxbranding import getMachineBrand, getMachineName, getBrandOEM
from ItalysatUtils import ItalysatGetSkinPath

class ItalyWifiModule(Screen):
    __module__ = __name__
    skin = '\n\t<screen position="center,center" size="634,474">\n\t\t\t<widget source="list" render="Listbox" position="12,6" size="611,424" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=3),\n\t\t\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t    <ePixmap pixmap="skin_default/buttons/red.png" position="158,433" size="140,40" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/green.png" position="368,433" size="140,40" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/green.png" position="578,433" size="140,40" alphatest="on" />\n\t\t    <widget name="key_red" position="157,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    <widget name="key_green" position="367,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    <widget name="key_yellow" position="577,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        if getMachineName() in ('dm800se', 'dm800sev2', 'dm8000', 'dm500hd', 'dm500hdv2', 'dm7020hd', 'dm7020hdv2'):
            self.modules = [('asix',
              'ASIX',
              'enigma2-plugin-drivers-network-usb-asix',
              True),
             ('ax88179_178a',
              'AX88179 HTC',
              'enigma2-plugin-drivers-network-usb-ax88179-178a',
              True),
             ('mt7650u_sta',
              'Ralink MT7610u',
              'enigma2-plugin-drivers-network-usb-mt7610u',
              True),
             ('r8712u',
              'Ralink RTL8712',
              'enigma2-plugin-drivers-network-usb-r8712u',
              True),
             ('rt73',
              'Realtek RT73',
              'enigma2-plugin-drivers-network-usb-rt73',
              True),
             ('rt2500usb',
              'Realtek RT2500',
              'enigma2-plugin-drivers-network-usb-rt2500',
              True),
             ('rt2800usb',
              'Realtek RT2800',
              'enigma2-plugin-drivers-network-usb-rt2800',
              True),
             ('rt5370sta',
              'Realtek RT3070',
              'enigma2-plugin-drivers-network-usb-rt3070',
              True),
             ('rt3573sta',
              'Realtek RT3573',
              'enigma2-plugin-drivers-network-usb-rt3573',
              True),
             ('rt5572sta',
              'Realtek RT5572',
              'enigma2-plugin-drivers-network-usb-rt5572',
              True),
             ('8188eu',
              'Ralink RTL8188eu',
              'enigma2-plugin-drivers-network-usb-rtl8188eu',
              True),
             ('8192cu',
              'Ralink RTL8192cu',
              'enigma2-plugin-drivers-network-usb-rtl8192cu',
              True),
             ('zd1211rw',
              'Zydas ZD1211',
              'enigma2-plugin-drivers-network-usb-zd1211rw',
              True)]
        elif getMachineName() in ('dm800', 'dm800hd'):
            self.modules = [('asix',
              'ASIX',
              'enigma2-plugin-drivers-network-usb-asix',
              True),
             ('ax88179_178a',
              'AX88179 HTC',
              'enigma2-plugin-drivers-network-usb-ax88179-178a',
              True),
             ('r8712u',
              'Ralink RTL8712',
              'enigma2-plugin-drivers-network-usb-r8712u',
              True),
             ('rt73',
              'Realtek RT73',
              'enigma2-plugin-drivers-network-usb-rt73',
              True),
             ('rt2500usb',
              'Realtek RT2500',
              'enigma2-plugin-drivers-network-usb-rt2500',
              True),
             ('rt2800usb',
              'Realtek RT2800',
              'enigma2-plugin-drivers-network-usb-rt2800',
              True),
             ('rt5370sta',
              'Realtek RT3070',
              'enigma2-plugin-drivers-network-usb-rt3070',
              True),
             ('rt3573sta',
              'Realtek RT3573',
              'enigma2-plugin-drivers-network-usb-rt3573',
              True),
             ('rt5572sta',
              'Realtek RT5572',
              'enigma2-plugin-drivers-network-usb-rt5572',
              True),
             ('zd1211b',
              'Zydas ZD1211B',
              'zd1211b',
              'zd1211b',
              True)]
        else:
            self.modules = [('ar5523',
              'Atheros 5523',
              'enigma2-plugin-drivers-network-usb-ar5523',
              True),
             ('ath',
              'ATH9K HTC',
              'enigma2-plugin-drivers-network-usb-ath9k-htc',
              True),
             ('carl9170',
              'Carl9170',
              'enigma2-plugin-drivers-network-usb-carl9170',
              True),
             ('mt7601Usta',
              'Ralink MT7601u',
              'enigma2-plugin-drivers-network-usb-mt7601u',
              True),
             ('r8712u',
              'Ralink RTL8712u',
              'enigma2-plugin-drivers-network-usb-r8712u',
              True),
             ('8723au',
              'Ralink RTL8723au',
              'enigma2-plugin-drivers-network-usb-r8723a',
              True),
             ('rt73usb',
              'Realtek RT73',
              'enigma2-plugin-drivers-network-usb-rt73',
              True),
             ('rt2500usb',
              'Realtek RT2500',
              'enigma2-plugin-drivers-network-usb-rt2500',
              True),
             ('rt2800usb',
              'Realtek RT2800',
              'enigma2-plugin-drivers-network-usb-rt2800',
              True),
             ('rt5370sta',
              'Realtek RT3070',
              'enigma2-plugin-drivers-network-usb-rt3070',
              True),
             ('rt3573sta',
              'Realtek RT3573',
              'enigma2-plugin-drivers-network-usb-rt3573',
              True),
             ('rt5572sta',
              'Realtek RT5572',
              'enigma2-plugin-drivers-network-usb-rt5572',
              True),
             ('rtl8187',
              'Ralink RTL8187',
              'enigma2-plugin-drivers-network-usb-rtl8187',
              True),
             ('8192cu',
              'Ralink RTL8192cu',
              'enigma2-plugin-drivers-network-usb-rtl8192cu',
              True),
             ('8812au',
              'Ralink RTL8812au',
              'enigma2-plugin-drivers-network-usb-rtl8812au',
              True),
             ('r8188eu',
              'Ralink RTL8188eu',
              'enigma2-plugin-drivers-network-usb-rtl8188eu',
              True),
             ('zd1211rw',
              'Zydas ZD1211',
              'enigma2-plugin-drivers-network-usb-zd1211rw',
              True),
             ('rtk_btusb',
              'Realtek Bluetooth RT8723',
              'rt8723bt',
              True)]
        self.modstatus = {}
        self.list = []
        self['key_red'] = Label(_('Remove'))
        self['key_green'] = Label(_('Restart E2'))
        self['key_yellow'] = Label(_('Remove all driver'))
        self['list'] = List(self.list)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.UninstallCheck,
         'green': self.runFinishedRe2,
         'yellow': self.removeAllQuestion,
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
            self.modstatus[mod[2]] = False

        system('/usr/bin/opkg list_installed > /tmp/status.log')
        try:
            f = open('/tmp/status.log', 'r')
            for line in f.readlines():
                for mod in self.modules:
                    if line.find(mod[2]) != -1:
                        self.modstatus[mod[2]] = True

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
                 False: skin_path + 'italy_icons/menu_off.png'}[self.modstatus.get(mod[2])])
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
            self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove "%s" ? (Note: Remove your DVB-T usb before pressing ok)') % sel)
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
        self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-depends --autoremove', callback)

    def removeComplete(self, result = None, retval = None, extra_args = None):
        sel = self['list'].getCurrent()[0]
        if sel:
            system('modprobe -rv ' + sel)
        self.message.close()
        self.updateList()

    def runFinishedRe2(self):
        msg = _('Enigma2 will be now hard restarted to activate WIFI.\nDo You want restart enigma2 now?')
        box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('Restart enigma'))

    def restartEnigma2(self, answer):
        if answer is True:
            system('killall -9 enigma2')

    def removeAllQuestion(self):
        msg = _('This function remove all WiFi drivers from your box.\nDo You want remove driver now?')
        box = self.session.openWithCallback(self.removeAll, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('WiFi remover'))

    def removeAll(self, answer):
        if answer is True:
            cmd = 'opkg remove --force-depends enigma2-plugin-drivers-network-usb-* ax88179-178a mt7601u mt7610u rt61 rt73 rt2870 rt3070 rt3573 rt5572 rt8723a rt8723bs rt8723bt rtl871x rtl8188eu rtl8192cu rtl8812au zd1211b kernel-module-ar5523 kernel-module-carl9170 kernel-module-usbnet kernel-module-asix kernel-module-ath9k-htc kernel-module-r8712u kernel-module-r8188eu kernel-module-rtl8192cu kernel-module-smsc75xx kernel-module-zd1211rw kernel-module-rt73usb kernel-module-rt5572sta kernel-module-rt5370sta kernel-module-rt3573sta kernel-module-rt2500usb kernel-module-rtl8187 kernel-module-rt2800usb kernel-module-8723au kernel-module-8812au kernel-module-8192cu kernel-module-mt7601usta kernel-module-ath kernel-module-ath9k-common kernel-module-ath9k-hw kernel-module-rt2800lib kernel-module-rt2x00lib kernel-module-rt2x00usb kernel-module-rtlwifi kernel-module-rtl8192c-common rt73-firmware firmware-ar5523 firmware-htc7010 firmware-htc9271 firmware-carl9170 firmware-rtl8712u firmware-rt2870 firmware-rt3070 firmware-rtl8188eu firmware-rtl8192cu firmware-zd1211 firmware-rt73'
            self.session.open(x_Console, title=_('WiFi Package Remove'), cmdlist=[cmd])
        self.updateList()