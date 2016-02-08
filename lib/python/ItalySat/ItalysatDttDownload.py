# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatDttDownload.py
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
from boxbranding import getMachineBrand, getMachineName, getBoxType
from ItalysatUtils import ItalysatGetSkinPath
from Components.About import about

class ItalyDttModule(Screen):
    __module__ = __name__
    skin = '\n\t<screen position="center,center" size="634,474">\n\t\t\t<widget source="list" render="Listbox" position="12,6" size="611,424" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=3),\n\t\t\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t    <ePixmap pixmap="skin_default/buttons/red.png" position="158,433" size="140,40" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/green.png" position="368,433" size="140,40" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/green.png" position="578,433" size="140,40" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/blue.png" position="788,433" size="140,40" alphatest="on" />\n\t\t    <widget name="key_red" position="157,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    <widget name="key_green" position="367,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    <widget name="key_yellow" position="577,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    <widget name="key_blue" position="787,433" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        if about.getKernelVersionString() <= '3.8.0':
            self.modules = [('dvb_usb_as102',
              'AS102',
              'enigma2-plugin-drivers-dvb-usb-as102',
              True),
             ('dvb_usb_af9015',
              'AF9015',
              'enigma2-plugin-drivers-dvb-usb-af9015',
              True),
             ('dvb_usb_af9035',
              'A867/AF9035',
              'enigma2-plugin-drivers-dvb-usb-af9035',
              True),
             ('dvb_usb_dib0700 ',
              'DIB0700',
              'enigma2-plugin-drivers-dvb-usb-dib0700',
              True),
             ('em28xx_dvb',
              'EM28xx',
              'enigma2-plugin-drivers-dvb-usb-em28xx',
              True),
             ('pctv452e',
              'PCTV452e',
              'enigma2-plugin-drivers-dvb-usb-pctv452e',
              True),
             ('dvb_usb_rtl2832',
              'RTL2832',
              'enigma2-plugin-drivers-dvb-usb-rtl2832',
              True),
             ('dvb_usb_it913x',
              'IT913x',
              'enigma2-plugin-drivers-dvb-usb-it913x',
              True),
             ('smsdvb',
              'Smsusb',
              'enigma2-plugin-drivers-dvb-usb-siano',
              True),
             ('dvb_usb_dtt200u',
              'Dtt200u',
              'enigma2-plugin-drivers-dvb-usb-dtt200u',
              True),
             ('dvb_usb_dw2102',
              'Dw2102',
              'enigma2-plugin-drivers-dvb-usb-dw2102',
              True),
             ('dvb_usb_nova_t_usb2',
              'Nova-T USB2',
              'kernel-module-dvb-usb-nova-t-usb2',
              True),
             ('dvb_usb_cinergyT2',
              'Cinergy T2',
              'kernel-module-dvb-usb-cinergyt2',
              True),
             ('dvb_usb_technisat_usb2',
              'Techinisat Usb2',
              'kernel-module-dvb-usb-technisat-usb2',
              True),
             ('dvb_usb_a800',
              'A800',
              'kernel-module-dvb-usb-a800',
              True),
             ('dvb_usb_dibusb_mb',
              'Dibusb Mb',
              'kernel-module-dvb-usb-dibusb-mb',
              False),
             ('dvb_usb_dibusb_mc',
              'Dibusb Mc',
              'kernel-module-dvb-usb-dibusb-mc',
              False),
             ('dvb_usb_umt_010',
              'Umt 010',
              'kernel-module-dvb-usb-umt-010',
              True),
             ('dvb_usb_cxusb',
              'Cxusb',
              'kernel-module-dvb-usb-cxusb',
              True),
             ('dvb_usb_m920x',
              'M920x',
              'kernel-module-dvb-usb-m920x',
              True),
             ('dvb_usb_gl861',
              'Gl861',
              'kernel-module-dvb-usb-gl861',
              True),
             ('dvb_usb_au6610',
              'Au6610',
              'kernel-module-dvb-usb-au6610',
              True),
             ('dvb_usb_digitv',
              'Digitv',
              'kernel-module-dvb-usb-digitv',
              True),
             ('dvb_usb_vp7045',
              'Vp7045',
              'kernel-module-dvb-usb-vp7045',
              True),
             ('dvb_usb_vp702x',
              'Vp702x',
              'kernel-module-dvb-usb-vp702x',
              True),
             ('dvb_usb_gp8psk',
              'Gp8psk',
              'kernel-module-dvb-usb-gp8psk',
              True),
             ('dvb_usb_ttusb2',
              'Ttusb2',
              'kernel-module-dvb-usb-ttusb2',
              True),
             ('dvb_usb_opera',
              'Opera',
              'kernel-module-dvb-usb-opera',
              True),
             ('dvb_usb_af9005',
              'AF9005',
              'kernel-module-dvb-usb-af9005',
              True),
             ('dvb_usb_anysee',
              'Anysee',
              'kernel-module-dvb-usb-anysee',
              True),
             ('dvb_usb_dtv5100',
              'Dtv5100',
              'kernel-module-dvb-usb-dtv5100',
              True),
             ('dvb_usb_ce6230',
              'Ce6230',
              'kernel-module-dvb-usb-ce6230',
              True),
             ('dvb_usb_friio',
              'Frioo',
              'kernel-module-dvb-usb-friio',
              True),
             ('dvb_usb_ec168',
              'Ec168',
              'kernel-module-dvb-usb-ec168',
              True),
             ('dvb_usb_az6027',
              'Az6027',
              'kernel-module-dvb-usb-az6027',
              True),
             ('dvb_usb_mxl111sf',
              'Mxl111sf',
              'kernel-module-dvb-usb-mxl111sf',
              True)]
        else:
            self.modules = [('dvb_usb_a867',
              'A867',
              'enigma2-plugin-drivers-dvb-usb-a867',
              True),
             ('dvb_usb_as102',
              'AS102',
              'enigma2-plugin-drivers-dvb-usb-as102',
              True),
             ('dvb_usb_af9015',
              'AF9015',
              'enigma2-plugin-drivers-dvb-usb-af9015',
              True),
             ('dvb_usb_af9035',
              'AF9035',
              'enigma2-plugin-drivers-dvb-usb-af9035',
              True),
             ('dvb_usb_dib0700 ',
              'Dib0700',
              'enigma2-plugin-drivers-dvb-usb-dib0700',
              True),
             ('em28xx_dvb',
              'Em28xx',
              'enigma2-plugin-drivers-dvb-usb-em28xx',
              True),
             ('pctv452e',
              'Pctv452e',
              'enigma2-plugin-drivers-dvb-usb-pctv452e',
              True),
             ('dvb_usb_rtl2832',
              'Rtl2832',
              'kernel-module-dvb-usb-rtl2832',
              True),
             ('dvb_usb_it913x',
              'It913x',
              'enigma2-plugin-drivers-dvb-usb-it913x',
              True),
             ('smsdvb',
              'Smsusb',
              'enigma2-plugin-drivers-dvb-usb-siano',
              True),
             ('dvb_usb_dtt200u',
              'Dtt200u',
              'enigma2-plugin-drivers-dvb-usb-dtt200u',
              True),
             ('dvb_usb_dw2102',
              'Dw2102',
              'enigma2-plugin-drivers-dvb-usb-dw2102',
              True),
             ('dvb_usb_nova_t_usb2',
              'Nova-T USB2',
              'kernel-module-dvb-usb-nova-t-usb2',
              True),
             ('dvb_usb_cinergyT2',
              'Cinergy T2',
              'kernel-module-dvb-usb-cinergyt2',
              True),
             ('dvb_usb_technisat_usb2',
              'Techinisat Usb2',
              'kernel-module-dvb-usb-technisat-usb2',
              True),
             ('dvb_usb_a800',
              'A800',
              'kernel-module-dvb-usb-a800',
              True),
             ('dvb_usb_dibusb_mb',
              'Dibusb Mb',
              'kernel-module-dvb-usb-dibusb-mb',
              False),
             ('dvb_usb_dibusb_mc',
              'Dibusb Mc',
              'kernel-module-dvb-usb-dibusb-mc',
              False),
             ('dvb_usb_umt_010',
              'Umt 010',
              'kernel-module-dvb-usb-umt-010',
              True),
             ('dvb_usb_cxusb',
              'Cxusb',
              'kernel-module-dvb-usb-cxusb',
              True),
             ('dvb_usb_m920x',
              'M920x',
              'kernel-module-dvb-usb-m920x',
              True),
             ('dvb_usb_gl861',
              'Gl861',
              'kernel-module-dvb-usb-gl861',
              True),
             ('dvb_usb_au6610',
              'Au6610',
              'kernel-module-dvb-usb-au6610',
              True),
             ('dvb_usb_digitv',
              'Digitv',
              'kernel-module-dvb-usb-digitv',
              True),
             ('dvb_usb_vp7045',
              'Vp7045',
              'kernel-module-dvb-usb-vp7045',
              True),
             ('dvb_usb_vp702x',
              'Vp702x',
              'kernel-module-dvb-usb-vp702x',
              True),
             ('dvb_usb_gp8psk',
              'Gp8psk',
              'kernel-module-dvb-usb-gp8psk',
              True),
             ('dvb_usb_ttusb2',
              'Ttusb2',
              'kernel-module-dvb-usb-ttusb2',
              True),
             ('dvb_usb_opera',
              'Opera',
              'kernel-module-dvb-usb-opera',
              True),
             ('dvb_usb_af9005',
              'AF9005',
              'kernel-module-dvb-usb-af9005',
              True),
             ('dvb_usb_anysee',
              'Anysee',
              'kernel-module-dvb-usb-anysee',
              True),
             ('dvb_usb_dtv5100',
              'Dtv5100',
              'kernel-module-dvb-usb-dtv5100',
              True),
             ('dvb_usb_ce6230',
              'Ce6230',
              'kernel-module-dvb-usb-ce6230',
              True),
             ('dvb_usb_friio',
              'Frioo',
              'kernel-module-dvb-usb-friio',
              True),
             ('dvb_usb_ec168',
              'Ec168',
              'kernel-module-dvb-usb-ec168',
              True),
             ('dvb_usb_az6027',
              'Az6027',
              'kernel-module-dvb-usb-az6027',
              True),
             ('dvb_usb_mxl111sf',
              'Mxl111sf',
              'kernel-module-dvb-usb-mxl111sf',
              True)]
        self.modstatus = {}
        self.list = []
        self['key_red'] = Label(_('Remove'))
        self['key_green'] = Label(_('Restart E2'))
        self['key_yellow'] = Label(_('Remove all driver'))
        self['key_blue'] = Label(_('Install all driver'))
        self['list'] = List(self.list)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.UninstallCheck,
         'green': self.runFinishedRe2,
         'yellow': self.removeAllQuestion,
         'blue': self.installAllQuestion,
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
        msg = _('Box will be now hard restarted to activate DVB-T.\nDo You want reboot now?')
        box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('Reboot'))

    def restartEnigma2(self, answer):
        if answer is True:
            system('killall -9 enigma2')

    def removeAllQuestion(self):
        msg = _('This function remove all DVB-T drivers from your box.\nDo You want remove driver now?')
        box = self.session.openWithCallback(self.removeAll, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('DVB-T remover'))

    def removeAll(self, answer):
        if answer is True:
            cmd = 'opkg remove --force-depends enigma2-plugin-drivers-dvb-usb-*'
            self.session.open(x_Console, title=_('DVB-T Package Remove'), cmdlist=[cmd])
        self.updateList()

    def installAllQuestion(self):
        msg = _('This function install all DVB-T drivers from your box.\nDo You want install all driver now? takes a long time, please be patient')
        box = self.session.openWithCallback(self.installAll, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('DVB-T installer'))

    def installAll(self, answer):
        if answer is True:
            cmd = 'opkg install --force-reinstall italysat-dvbt-all'
            self.session.open(x_Console, title=_('DVB-T Package Install'), cmdlist=[cmd])
        self.updateList()