# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatBlue.py
from Screens.Screen import Screen
from enigma import eTimer, eDVBCI_UI, iServiceInformation, eConsoleAppContainer
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageVersion, getImageBuild
from Components.About import about
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Console import Console
from Components.ConfigList import ConfigList
from Components.config import config, ConfigSubsection, ConfigText, ConfigSelection, getConfigListEntry, ConfigNothing, KEY_LEFT, KEY_RIGHT, KEY_OK, NoSave
from Components.FileList import FileList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Renderer.Picon import getPiconName
from ServiceReference import ServiceReference
from Screens.MessageBox import MessageBox
from Screens.ParentalControlSetup import ParentalControlSetup
from Tools.Directories import fileExists
from ItalysatSettings import ItalysatSettings
from ItalysatUtils import ItalysatUtils
import os, thread
t = ItalysatUtils()
OEVER = '2.0'
IMAGEVER = getImageVersion()
IMAGEBUILD = getImageBuild()
KERNELVER = about.getKernelVersionString()

class ItalysatBlue(Screen):
    skin = '\n\t<screen name="ItalysatBlue" position="center,center" size="1013,482">\n\t  <widget name="info_key" position="24,22" zPosition="2" size="445,30" halign="center" font="Regular;19" foregroundColor="blue" />\n\t  <widget name="config" position="24,58" size="445,83" zPosition="2" transparent="1" />\n\t  <widget source="Title" render="Label" position="521,41" size="474,30" font="Regular;19" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t  <widget source="conninfo" render="Label" position="16,310" size="473,30" font="Regular;19" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t  <widget source="conn" render="Label" position="16,310" size="473,30" font="Regular;19" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t  <widget name="lab1" position="24,153" size="445,30" font="Regular;24" zPosition="2" backgroundColor="#00333333" transparent="1" />\n\t  <widget name="lab2" position="24,187" size="445,30" font="Regular;24" zPosition="2" backgroundColor="#00333333" transparent="1" />\n\t  <widget name="lab3" position="24,226" size="445,30" font="Regular;24" zPosition="2" backgroundColor="#00333333" transparent="1" />\n\t  <widget name="lab4" position="24,268" size="445,30" font="Regular;24" zPosition="2" backgroundColor="#00333333" transparent="1" />\n\t  <widget name="info_ecm" position="521,100" size="479,266" font="Regular; 19" zPosition="2" backgroundColor="#00333333" transparent="1" halign="left" />\n\t  <ePixmap position="63,390" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="on" />\n\t  <ePixmap position="310,390" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" />\n\t  <ePixmap position="554,390" size="140,40" pixmap="skin_default/buttons/yellow.png" alphatest="on" />\n\t  <ePixmap position="770,390" size="140,40" pixmap="skin_default/buttons/blue.png" alphatest="on" />\n\t  <widget name="key_red" position="63,390" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t  <widget name="key_green" position="310,390" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t  <widget name="key_yellow" position="556,390" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t  <widget name="key_blue" position="770,390" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['config'] = ConfigList(self.list)
        self['conninfo'] = StaticText('')
        self['conn'] = Label('')
        self['conn'].hide()
        self['info_key'] = Label(_('Use arrows < > to select'))
        self['lab1'] = Label()
        self['lab2'] = Label()
        self['lab3'] = Label()
        self['lab4'] = Label()
        self['info_ecm'] = ScrollLabel('')
        self['key_red'] = Label(_('Settings'))
        self['key_green'] = Label(_('Backup'))
        self['key_yellow'] = Label(_('Timeline'))
        self['key_blue'] = Label(_('Weather Set'))
        self['actions'] = NumberActionMap(['ColorActions',
         'CiSelectionActions',
         'WizardActions',
         'SetupActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'ok': self.ok_pressed,
         'back': self.close,
         'red': self.keyred,
         'green': self.keygreen,
         'yellow': self.keyyellow,
         'blue': self.keyblue}, -1)
        self.console = Console()
        self.nemPortNumber = t.readPortNumber()
        self.ecmTimer = eTimer()
        self.ecmTimer.timeout.get().append(self.readEcmInfo)
        self.ecmTimer.start(1000, False)
        self.onLayoutFinish.append(self.checkdeveloperMode)
        self.onShown.append(self.setWindowTitle)
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.linkAddons = t.readAddonsUrl()[0]
        thread.start_new_thread(self.readEcmInfo, ())

    def setWindowTitle(self):
        self.setTitle('%s - %s: %s - SVN: (%s)' % (_('ItalySat'),
         _('Image Version'),
         IMAGEVER,
         IMAGEBUILD))

    def checkdeveloperMode(self):
        self.loadEmuList()
        if config.italysat.skindevelopermode.value:
            self['conn'].show()
            self['conn'].setText(_('!!!! WARNING !!!!\n\nYou are using image in developer mode\nPlease disable it for best performance\nPress: Menu-> Config-> System-> Italy Image Option: SkinDeveloperMode to disable it.'))
        else:
            self['conn'].hide()
            self['conn'].setText('')

    def runFinished(self, retval):
        if fileExists('/tmp/info.txt') and retval == 0:
            self['conninfo'].text = ''
            self.session.open(italysatShowPanel, '/tmp/info.txt', _('ItalySat Timeline'))
            os.unlink('/tmp/info.txt')
        else:
            self['conninfo'].text = _('Server not found! Please check internet connection.')

    def keyred(self):
        self.session.openWithCallback(self.loadEmuList, ItalysatSettings)

    def keygreen(self):
        from Plugins.SystemPlugins.ItalyCore.ui import ItalyMenu
        self.session.openWithCallback(self.loadEmuList, ItalyMenu)

    def keyyellow(self):
        if self.container.running():
            self.container.kill()
        if not self.container.running():
            self['conninfo'].text = _('Connetting to server. Please wait...')
            cmd = 'wget http://feeds.italysat.eu/timeline.txt -O /tmp/info.txt'
            self.container.execute(cmd)

    def keyblue(self):
        from ItalySat.ItalysatWeatherSearch import WeatherSearch
        self.session.openWithCallback(self.loadEmuList, WeatherSearch)

    def keyLeft(self):
        self['config'].handleKey(KEY_LEFT)

    def keyRight(self):
        self['config'].handleKey(KEY_RIGHT)

    def loadEmuList(self):
        emu = []
        crd = []
        emu.append('None')
        crd.append('None')
        self.emu_list = {}
        self.crd_list = {}
        self.emu_list['None'] = 'None'
        self.crd_list['None'] = 'None'
        emufilelist = FileList('/usr/emuscript', matchingPattern='_em.*')
        srvfilelist = FileList('/usr/emuscript', matchingPattern='_cs.*')
        for x in emufilelist.getFileList():
            if x[0][1] != True:
                emuName = t.readEmuName(x[0][0][:-6])
                emu.append(emuName)
                self.emu_list[emuName] = x[0][0][:-6]

        softcam = ConfigSelection(default=t.readEmuName(t.readEmuActive()), choices=emu)
        for x in srvfilelist.getFileList():
            if x[0][1] != True:
                srvName = t.readSrvName(x[0][0][:-6])
                crd.append(srvName)
                self.crd_list[srvName] = x[0][0][:-6]

        cardserver = ConfigSelection(default=t.readSrvName(t.readSrvActive()), choices=crd)
        del self.list[:]
        self.list.append(getConfigListEntry(_('SoftCams (%s) :') % str(len(emu) - 1), softcam))
        self.list.append(getConfigListEntry(_('CardServers (%s) :') % str(len(crd) - 1), cardserver))
        self.list.append(getConfigListEntry(_('About ItalySat'), ConfigNothing()))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def ok_pressed(self):
        if self.container.running():
            self.container.kill()
        self.sel = self['config'].getCurrentIndex()
        if self.sel == 0:
            self.newemu = self.emu_list[self['config'].getCurrent()[1].getText()]
            self.ss_sc()
        elif self.sel == 1:
            self.newsrv = self.crd_list[self['config'].getCurrent()[1].getText()]
            self.ss_srv()
        elif self.sel == 2:
            self.session.open(ItalyAbout)

    def ss_sc(self):
        self.emuactive = t.readEmuActive()
        self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
        if self.emuactive != 'None' and self.newemu != 'None':
            if self.emuactive == self.newemu:
                mess = _('Restarting %s.') % t.readEmuName(self.emuactive)
            else:
                mess = _('Stopping %s and starting %s.') % (t.readEmuName(self.emuactive), t.readEmuName(self.newemu))
            cmd = '/usr/emuscript/%s_em.sh stop && ' % self.emuactive
            cmd += '/usr/emuscript/%s_em.sh start && ' % self.newemu
            cmd += 'rm -f /var/bin/emudefault && '
            cmd += 'echo %s > /var/bin/emudefault && ' % self.newemu
            cmd += 'echo %s > /etc/CurrentItalyCamName' % self.newemu
            self.executeCommand(mess, cmd, True, True)
            return
        if self.emuactive != 'None':
            mess = _('Stopping %s.') % t.readEmuName(self.emuactive)
            cmd = '/usr/emuscript/%s_em.sh stop && ' % self.emuactive
            cmd += 'rm -f /var/bin/emudefault && '
            cmd += 'rm -f /etc/CurrentItalyCamName'
            self.executeCommand(mess, cmd)
            return
        if self.newemu != 'None':
            mess = _('Starting %s.') % t.readEmuName(self.newemu)
            cmd = '/usr/emuscript/%s_em.sh start && ' % self.newemu
            cmd += 'rm -f /var/bin/emudefault && '
            cmd += 'echo %s > /var/bin/emudefault && ' % self.newemu
            cmd += 'echo %s > /etc/CurrentItalyCamName' % self.newemu
            self.executeCommand(mess, cmd, True, True)

    def ss_srv(self):
        self.serveractive = t.readSrvActive()
        if self.serveractive == 'None' and self.newsrv == 'None':
            return
        self.emuactive = t.readEmuActive()
        if self.emuactive != 'None' and self.serveractive == 'None':
            self.box = self.session.open(MessageBox, _('Please stop %s\nbefore start Cardserver!') % t.readEmuName(self.emuactive), MessageBox.TYPE_INFO)
            self.box.setTitle(_('Start Cardserver'))
            return
        if self.serveractive != 'None' and self.newsrv != 'None':
            if self.serveractive == self.newsrv:
                mess = _('Restarting %s.') % t.readSrvName(self.serveractive)
            else:
                mess = _('Stopping %s and starting %s.') % (t.readSrvName(self.serveractive), t.readSrvName(self.newsrv))
            cmd = '/usr/emuscript/%s_cs.sh stop && ' % self.serveractive
            cmd += '/usr/emuscript/%s_cs.sh start && ' % self.newsrv
            cmd += 'rm -f /var/bin/csdefault && '
            cmd += 'echo %s > /var/bin/csdefault && ' % self.newsrv
            cmd += 'echo %s > /etc/CurrentItalyCamName' % self.newsrv
            self.executeCommand(mess, cmd)
            return
        if self.serveractive != 'None':
            mess = _('Stopping %s.') % t.readSrvName(self.serveractive)
            cmd = '/usr/emuscript/%s_cs.sh stop && ' % self.serveractive
            cmd += 'rm -f /var/bin/csdefault && '
            cmd += 'rm -f /var/bin/CurrentItalyCamName'
            self.executeCommand(mess, cmd)
            return
        if self.newsrv != 'None':
            mess = _('Starting  %s.') % t.readSrvName(self.newsrv)
            cmd = '/usr/emuscript/%s_cs.sh start && ' % self.newsrv
            cmd += 'rm -f /var/bin/csdefault && '
            cmd += 'echo %s > /var/bin/csdefault && ' % self.newsrv
            cmd += 'echo %s > /etc/CurrentItalyCamName' % self.newsrv
            self.executeCommand(mess, cmd)

    def executeCommand(self, mess, cmd, panelClose = False, playServ = False):
        self.playServ = playServ
        self.panelClose = panelClose
        self.hide()
        self.mbox = self.session.open(MessageBox, mess, MessageBox.TYPE_INFO, enable_input=False)
        self.mbox.setTitle(_('Running..'))
        if self.playServ:
            self.session.nav.stopService()
        self.console.ePopen("italysatc '%s' '%s' '%s'" % ('127.0.0.1', self.nemPortNumber, cmd), self.commandFinished)

    def commandFinished(self, result, retval, extra_args):
        if self.playServ:
            self.session.nav.playService(self.oldref)
        self.mbox.close()
        if self.panelClose:
            self.close()
        else:
            self.show()

    def readEcmInfo(self):
        name = 'N/A'
        provider = 'N/A'
        aspect = 'N/A'
        videosize = 'N/A'
        myserviceinfo = ''
        myservice = self.session.nav.getCurrentService()
        if myservice is not None:
            myserviceinfo = myservice.info()
            if self.session.nav.getCurrentlyPlayingServiceReference():
                name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
            provider = self.getServiceInfoValue(iServiceInformation.sProvider, myserviceinfo)
            aspect = self.getServiceInfoValue(iServiceInformation.sAspect, myserviceinfo)
            if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
                aspect = '4:3'
            else:
                aspect = '16:9'
            if myserviceinfo:
                width = myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoWidth) or -1
                height = myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoHeight) or -1
                if width != -1 and height != -1:
                    videosize = '%dx%d' % (width, height)
        self['lab1'].setText(_('Name: ') + name)
        self['lab2'].setText(_('Provider: ') + provider)
        self['lab3'].setText(_('Aspect Ratio: ') + aspect)
        self['lab4'].setText(_('Videosize: ') + videosize)
        service = self.session.nav.getCurrentService()
        if service:
            info = service.info()
            if info is not None:
                info.getInfo(iServiceInformation.sIsCrypted) and self['info_ecm'].setText(t.readEcmInfo())
            else:
                self['info_ecm'].setText('Free To Air')
        else:
            self['info_ecm'].setText('')
        return

    def getServiceInfoValue(self, what, myserviceinfo):
        if myserviceinfo is None:
            return ''
        else:
            v = myserviceinfo.getInfo(what)
            if v == -2:
                v = myserviceinfo.getInfoString(what)
            elif v == -1:
                v = 'N/A'
            return v

    def myclose(self):
        self.close()


class italysatShowPanel(Screen):
    skin = '\n\t<screen name="italysatShowPanel" position="center,center" size="990,599">\n\t\t<eLabel position="-2,-1" size="900,2" backgroundColor="#3366cc" zPosition="5" />\n\t\t<widget source="list" render="Listbox" position="10,13" size="966,527" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t<convert type="StringList" />\n\t\t</widget>\n\t\t<eLabel position="0,560" size="991,2" backgroundColor="#3366cc" zPosition="5" />\n\t\t<widget name="close" position="0,560" zPosition="1" size="991,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t</screen>'
    __module__ = __name__

    def __init__(self, session, file, Wtitle):
        Screen.__init__(self, session)
        self.file = file
        self.Wtitle = Wtitle
        self.list = []
        self['close'] = Label(_('Close'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
         'ok': self.openDetails,
         'back': self.close})
        self.loadData()
        self['list'] = List(self.list)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(self.Wtitle)

    def loadData(self):
        try:
            f = open(self.file, 'r')
            for line in f.readlines():
                self.list.append(line)

            f.close()
        except:
            mess = _('File: %s not found!') % self.file
            self.list.append(mess)

    def openDetails(self):
        message = self['list'].getCurrent()
        if message:
            mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
            mbox.setTitle(_('Details'))


class ItalyAbout(Screen):
    skin = '\n\t<screen position="center,center" size="970,560">\n\t  <widget name="about" position="22,19" size="922,519" font="Regular;20" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['about'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'DirectionActions'], {'back': self.close,
         'ok': self.close,
         'up': self['about'].pageUp,
         'left': self['about'].pageUp,
         'down': self['about'].pageDown,
         'right': self['about'].pageDown})
        self['about'].hide()
        self.updatetext()
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('ItalySat About'))

    def updatetext(self):
        message = '\nItalySat Version: %s OE(%s)' % (IMAGEVER, OEVER)
        message += '\n\nImage version: ' + IMAGEVER
        message += '\nBased on Enigma Version: ' + IMAGEBUILD
        message += '\nKernel version: ' + KERNELVER
        message += '\n\nFor support visit: http://www.italysat.eu/'
        message += '\nEMAIL: italysat.official@gmail.com'
        message += '\nFacebook: https://www.facebook.com/ItalySat'
        message += '\nTwitter: https://twitter.com/italysat'
        message += '\n\nCreated by italysat.eu - Italian Team'
        message += '\nBuild by Bobsilvio and Ph0eniX (Coder)'
        message += '\nThanks to:'
        message += '\nNeo_3 (Skinner)'
        message += '\nMobo (Moderator)'
        message += '\nSantino91 (Moderator)'
        message += '\nRealstone (Moderator)'
        self['about'].show()
        self['about'].setText(message)


class ItalyBluePanel():

    def __init__(self):
        self['ItalyBluePanel'] = ActionMap(['InfobarExtensions'], {'ItalyBluePanelshow': self.showItalyBluePanel})

    def showItalyBluePanel(self):
        self.session.openWithCallback(self.callItaAction, ItalysatBlue)

    def callItaAction(self, *args):
        if len(args):
            actionmap, context, action = args
            actionmap.action(context, action)