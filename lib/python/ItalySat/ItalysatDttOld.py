# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatDttOld.py
from Screens.Screen import Screen
from Screens.Console import Console
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigNumber, ConfigSelection, ConfigClock, NoSave, configfile
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, createDir, resolveFilename, SCOPE_SKIN_IMAGE
from os import system, statvfs, remove as os_remove, rename as os_rename, stat as mystat, popen, getcwd, chdir, listdir
from ItalysatUtils import ItalysatGetSkinPath, italysat_get_Version
from ItalysatDownloader import ItalyDownloader
from boxbranding import getBoxType
import time
import datetime

class ItalysatDttPanel(Screen):
    skin = '\n\t<screen name="ItalySat DTT Manager" position="center,147" size="817,427" title="ItalySat Usb DTT Manager">\n\t  <widget name="driverinfo" position="211,70" size="185,27" font="Regular;24" halign="center" valign="center" backgroundColor="blue" foregroundColor="black" />\n\t  <widget name="updateinfo" position="559,72" size="186,27" font="Regular;24" valign="center" halign="center" backgroundColor="blue" foregroundColor="black" />\n\t  <widget name="tuner1" position="14,99" size="112,48" font="Regular;24" halign="center" valign="center" backgroundColor="blue" foregroundColor="black" />\n\t  <widget name="tuner2" position="14,157" size="112,48" font="Regular;24" valign="center" halign="center" backgroundColor="blue" foregroundColor="black" />\n\t  <widget name="firstdrv" position="151,102" size="309,48" font="Regular;24" halign="center" valign="center" transparent="1" />\n\t  <widget name="seconddrv" position="151,155" size="309,48" font="Regular;24" halign="center" valign="center" transparent="1" />\n\t  <widget name="firstdate" position="493,102" size="309,48" font="Regular;24" valign="center" halign="center" transparent="1" />\n\t  <widget name="seconddate" position="493,155" size="309,48" font="Regular;24" valign="center" halign="center" transparent="1" />\n\t  <widget name="lab3" position="271,259" size="287,32" font="Regular;24" halign="center" valign="center" transparent="1" />\n\t  <widget name="labstop" position="347,298" size="140,32" zPosition="1" font="Regular;24" valign="center" halign="center" backgroundColor="red" foregroundColor="black" />\n\t  <widget name="labstart" position="347,298" size="140,32" zPosition="1" font="Regular;24" valign="center" halign="center" backgroundColor="green" foregroundColor="black" />\n\t  <ePixmap position="82,374" size="138,38" pixmap="skin_default/buttons/red.png" alphatest="on" zPosition="1" />\n\t  <ePixmap position="348,374" size="138,38" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />\n\t  <ePixmap position="600,372" size="138,38" pixmap="skin_default/buttons/yellow.png" alphatest="on" zPosition="1" />\n\t  <widget name="key_red" position="82,374" zPosition="2" size="138,38" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />\n\t  <widget name="key_green" position="348,374" zPosition="2" size="139,34" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />\n\t  <widget name="key_yellow" position="600,372" zPosition="2" size="138,34" font="Regular;20" halign="center" valign="center" backgroundColor="yellow" transparent="1" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.firstdrv = 'Driver Not Installed'
        self.seconddrv = 'Driver Not Installed'
        self.firstdate = 'Driver Not Installed'
        self.seconddate = 'Driver Not Installed'
        self['firstdrv'] = Label(self.firstdrv)
        self['seconddrv'] = Label(self.seconddrv)
        self['firstdate'] = Label(self.firstdate)
        self['seconddate'] = Label(self.seconddate)
        self['driverinfo'] = Label(_('DRIVER'))
        self['updateinfo'] = Label(_('UPDATED TO'))
        self['tuner1'] = Label(_('Tuner 1'))
        self['tuner2'] = Label(_('Tuner 2'))
        self['lab3'] = Label(_('Check Current Status:'))
        self['labstop'] = Label(_('Disabled'))
        self['labstart'] = Label(_('Driver Up'))
        self['key_red'] = Label(_('Disable'))
        self['key_green'] = Label(_('Enable'))
        self['key_yellow'] = Label(_('Download'))
        self.my_dtt_active = False
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.close,
         'red': self.MeStop,
         'green': self.MeStart,
         'yellow': self.MeInstall})
        self.onLayoutFinish.append(self.updateMe)

    def MeInstall(self):
        self.session.openWithCallback(self.updateMe, ItalysatDttConf)

    def myclose(self):
        self.activityTimer.stop()
        del self.activityTimer
        mybox = self.session.openWithCallback(self.domyclose, MessageBox, _('Sorry, This panel is only for Dreambox DM800'), type=MessageBox.TYPE_INFO)
        mybox.setTitle('Info')

    def domyclose(self, ret):
        self.close()

    def updateMe(self):
        self.firstdrv = _('Driver Not Installed')
        if fileExists('/usr/bin/italysatDtt.sh'):
            fileExists('/usr/bin/italysatDtt.sh')
            f = open('/usr/bin/italysatDtt.sh', 'r')
            for line in f.readlines():
                if line.find('#driver:') != -1:
                    parts = line.strip().split(':')
                    self.firstdrv = parts[1]
                    break

            f.close()
        self.seconddrv = ''
        if fileExists('/usr/bin/italysatDtt.sh'):
            fileExists('/usr/bin/italysatDtt.sh')
            f = open('/usr/bin/italysatDtt.sh', 'r')
            for line in f.readlines():
                if line.find('#driver2:') != -1:
                    parts = line.strip().split(':')
                    self.seconddrv = parts[1]
                    break

            f.close()
        self.firstdate = _('Driver Not Installed')
        if fileExists('/lib/modules/italysat/date.txt'):
            fileExists('/lib/modules/italysat/date.txt')
            f = open('/lib/modules/italysat/date.txt', 'r')
            for line in f.readlines():
                if line.find('#DATE:') != -1:
                    parts = line.strip().split(':')
                    self.firstdate = parts[1]
                    break

            f.close()
        self.seconddate = ''
        if fileExists('/lib/modules/italysat/date2.txt'):
            fileExists('/lib/modules/italysat/date2.txt')
            f = open('/lib/modules/italysat/date2.txt', 'r')
            for line in f.readlines():
                if line.find('#DATE:') != -1:
                    parts = line.strip().split(':')
                    self.seconddate = parts[1]
                    break

            f.close()
        self['firstdrv'].setText(self.firstdrv)
        self['seconddrv'].setText(self.seconddrv)
        self['firstdate'].setText(self.firstdate)
        self['seconddate'].setText(self.seconddate)
        self['labstart'].hide()
        self['labstop'].hide()
        self.my_dtt_active = False
        f = open('/usr/bin/enigma2.sh', 'r')
        for line in f.readlines():
            if line.find('italysatDtt.sh') != -1:
                self.my_dtt_active = True
                continue

        f.close()
        if self.my_dtt_active == True:
            self['labstop'].hide()
            self['labstart'].show()
        else:
            self['labstop'].show()
            self['labstart'].hide()

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

    def MeStart(self):
        if self.firstdrv == _('Driver Not Installed'):
            nobox = self.session.open(MessageBox, _('You need to download a driver before you start'), MessageBox.TYPE_INFO)
            nobox.setTitle('Info')
        elif self.my_dtt_active == False:
            m = "echo -e '\n\nI try to start the drivers..\n\nPlease wait..\n'"
            m1 = '/usr/bin/italysatDtt.sh'
            m2 = 'sleep 2'
            self.session.open(Console, title='Dtt', cmdlist=[m, m1, m2], finishedCallback=self.MeStart2)

    def MeStart2(self):
        check = True
        if check == True:
            out = open('/usr/bin/enigma2sh.tmp', 'w')
            f = open('/usr/bin/enigma2.sh', 'r')
            for line in f.readlines():
                if line.find('italysatDtt.sh') != -1:
                    continue
                if line.find('cd /home/root') != -1:
                    out.write('/usr/bin/italysatDtt.sh\n')
                out.write(line)

            f.close()
            out.close()
            os_rename('/usr/bin/enigma2sh.tmp', '/usr/bin/enigma2.sh')
            system('chmod 0755 /usr/bin/enigma2.sh')
            message = _('Driver Up, restart E2 to start DVB-T tuner.\nRestart Enigma now?')
            ybox = self.session.openWithCallback(self.restEn, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle('Enigma2 Restart.')
        else:
            mybox = self.session.open(MessageBox, _('Sorry, No Supported USB DTT found. \nReboot and Retries Enabled'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
            self.close()

    def MeStop(self):
        if self.my_dtt_active == True:
            out = open('/usr/bin/enigma2sh.tmp', 'w')
            f = open('/usr/bin/enigma2.sh', 'r')
            for line in f.readlines():
                if line.find('italysatDtt.sh') != -1:
                    continue
                out.write(line)

            f.close()
            out.close()
            os_rename('/usr/bin/enigma2sh.tmp', '/usr/bin/enigma2.sh')
            system('chmod 0755 /usr/bin/enigma2.sh')
            message = _('Tuner deactivation need a reboot to take effects.\nReboot your stb now?')
            ybox = self.session.openWithCallback(self.restBo, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle('Reboot.')

    def restEn(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def restBo(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 2)
        else:
            self.close()


class ItalysatDttConf(Screen):
    skin = '\n\t<screen name="ItalysatDttConf" position="center,center" size="800,520" title="ItalySat Usb Tuners Config">\n\t  <widget source="list" render="Listbox" position="20,20" size="760,440" scrollbarMode="showOnDemand">\n\t    <convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (90, 25), size = (690, 80), font=0, text = 0),\n\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (0, 3), size = (80, 80), png = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 24),gFont("Regular", 24)],\n\t\t\t\t\t\t"itemHeight": 86\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t  </widget>\n\t  <ePixmap position="183,469" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="on" zPosition="1" />\n\t  <ePixmap position="465,469" size="140,40" pixmap="skin_default/buttons/yellow.png" alphatest="on" zPosition="1" />\n\t  <widget name="key_red" position="182,468" zPosition="2" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="transpBlack" transparent="1" />\n\t  <widget name="key_yellow" position="464,467" zPosition="2" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="transpBlack" transparent="1" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Label(_('Continue'))
        self['key_yellow'] = Label(_('Cancel'))
        self.list = []
        self['list'] = List(self.list)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'back': self.close,
         'ok': self.KeyOk,
         'red': self.KeyOk,
         'yellow': self.close})
        self.updateList()

    def updateList(self):
        self.list = []
        mypath = ItalysatGetSkinPath()
        mypixmap = mypath + 'italy_icons/onepen.png'
        png = LoadPixmap(mypixmap)
        name = 'One Usb MonoTuner'
        idx = 0
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/onepen.png'
        png = LoadPixmap(mypixmap)
        name = 'One Usb DualTuner'
        idx = 1
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/twopen.png'
        png = LoadPixmap(mypixmap)
        name = 'Two Usb Same Models'
        idx = 2
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + 'italy_icons/twopen2.png'
        png = LoadPixmap(mypixmap)
        name = 'Two Usb Different Models'
        idx = 3
        res = (name, png, idx)
        self.list.append(res)
        self['list'].list = self.list

    def KeyOk(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            self.sel = self.sel[2]
            self.session.open(ItalysatDttDriversList, self.sel)
        self.close()


class ItalysatDttDriversList(Screen):
    skin = '\n\t<screen position="center,center" size="860,540" title="Usb Tuner Available Drivers">\n\t\t<widget source="list" render="Listbox" position="10,10" size="840,500" scrollbarMode="showOnDemand" >\n\t\t\t<convert type="StringList" />\n\t\t</widget>\n\t\t<widget name="connection" position="10,500" size="840,30" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t</screen>'

    def __init__(self, session, device):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['connection'] = Label(_('Please wait, connection to server in progress....'))
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.myinstall,
         'back': self.close})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.Listconn)
        self.activityTimer.start(1, False)
        self.onClose.append(self.delTimer)
        self.progress = 0
        self.device = device
        self.mainconf = _('One Usb DTT MonoTuner')
        if self.device == 1:
            self.mainconf = _('One Usb DTT DualTuner')
        elif self.device == 2:
            self.mainconf = _('Two Usb DTT Same Models')
        elif self.device == 3:
            self.mainconf = _('Two Usb DTT Different Models')

    def delTimer(self):
        del self.activityTimer

    def ItalysatDtt_geturl(self):
        path = 'http://sources.italysat.eu/dm800-dtt'
        return path

    def Listconn(self):
        self.activityTimer.stop()
        url = self.ItalysatDtt_geturl()
        url += '/listadtt.cfg'
        cmd = 'wget -O /tmp/italist.tmp ' + url
        rc = system(cmd)
        strview = ''
        if fileExists('/tmp/italist.tmp'):
            f = open('/tmp/italist.tmp', 'r')
            for line in f.readlines():
                if line.find(';') != -1:
                    parts = line.strip().split(';')
                    text = parts[0].strip() + ': ' + parts[1].strip()
                    file = parts[2].strip()
                    res = (text, file)
                    self.list.append(res)

            f.close()
            os_remove('/tmp/italist.tmp')
            self['list'].list = self.list
        else:
            mybox = self.session.open(MessageBox, _('Sorry. Connection to the italysat.eu Server failed.\nCheck that your internet connection please.\n(Maybe the server download is off)'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
        self['connection'].hide()

    def myinstall(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            message = _('Do you want install the Driver:\n ') + self.sel[0] + ' ?'
            ybox = self.session.openWithCallback(self.confpen, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle('Installation Confirm')

    def confpen(self, answer):
        if answer is True:
            if self.device == 0:
                self.compose_mono('1')
            elif self.device == 1:
                self.compose_mono('2')
            elif self.device == 2:
                self.compose_mono('2')
            elif self.device == 3:
                if self.progress == 0:
                    self.progress = 1
                    self.compose_mono('3')
                else:
                    self.compose_dual()

    def write_cfg(self):
        out = open('/etc/italysatDtt.cfg', 'w')
        out.write(self.mainconf)
        out.close()

    def compose_mono(self, answer):
        system('rm -f /lib/modules/italysat/*')
        system('rm -f /usr/bin/italysatDtt.sh')
        url = self.ItalysatDtt_geturl()
        file = self.sel[1]
        file = file.strip()
        url = url + '/' + file
        cmd = 'wget -O /tmp/' + file + ' ' + url
        rc = system(cmd)
        dest = '/tmp/' + file
        mydir = getcwd()
        chdir('/')
        cmd = 'tar -xjf ' + dest
        rc = system(cmd)
        chdir(mydir)
        cmd = 'rm -f ' + dest
        rc = system(cmd)
        system('chmod 0755 /usr/bin/italysatDtt.sh')
        if answer == '3':
            os_rename('/usr/bin/italysatDtt.sh', '/usr/bin/italysatDtt2.tmp2')
            os_rename('/lib/modules/italysat/date.txt', '/lib/modules/italysat/date2.txt')
            mybox = self.session.open(MessageBox, _('First tuner drivers installed.\n You can now select drivers for second tuner'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
        else:
            self.write_cfg()
            mybox = self.session.open(MessageBox, _('Driver Successfully Installed.\n You can now Enable your Usb tuner'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
            self.close()

    def compose_dual(self):
        newdrivers = ''
        driver = ''
        url = self.ItalysatDtt_geturl()
        file = self.sel[1]
        file = file.strip()
        url = url + '/' + file
        cmd = 'wget -O /tmp/' + file + ' ' + url
        rc = system(cmd)
        dest = '/tmp/' + file
        mydir = getcwd()
        chdir('/')
        cmd = 'tar -xjf ' + dest
        rc = system(cmd)
        chdir(mydir)
        cmd = 'rm -f ' + dest
        rc = system(cmd)
        f = open('/usr/bin/italysatDtt.sh', 'r')
        check = 0
        for line in f.readlines():
            if line.find('#driver:') != -1:
                driver = line[8:]
            if line.find('# fine insmod') != -1:
                break
            if check == 1:
                newdrivers = newdrivers + line
            if line.find('# inizio insmod') != -1:
                check = 1

        f.close()
        out = open('/usr/bin/italysatDtt.sh', 'w')
        f = open('/usr/bin/italysatDtt2.tmp2', 'r')
        for line in f.readlines():
            if line.find('#driver2:') != -1:
                line = line.strip() + driver
            if line.find('# fine insmod') != -1:
                out.write(newdrivers)
            out.write(line)

        f.close()
        out.close()
        system('chmod 0755 /usr/bin/italysatDtt.sh')
        system('rm -f /usr/bin/italysatDtt2.tmp2')
        self.write_cfg()
        mybox = self.session.open(MessageBox, _('Drivers for Tuner1 and Tuner2 successfully installed.\n You can now Enable your tuners'), MessageBox.TYPE_INFO)
        mybox.setTitle(_('Info'))
        self.close()