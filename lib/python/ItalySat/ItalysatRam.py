# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatRam.py
from Screens.Screen import Screen
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from os import system
from enigma import eTimer
from Components.ProgressBar import ProgressBar
from boxbranding import getMachineName
config.plugins.ClearMem = ConfigSubsection()
config.plugins.ClearMem.enable = ConfigYesNo(default=False)
NGETTEXT = False
try:
    ngettext('%d minute', '%d minutes', 5)
    NGETTEXT = True
except Exception as e:
    print '[ClearMem] ngettext is not supported:', e

choicelist = []
for i in range(5, 151, 5):
    if NGETTEXT:
        choicelist.append(('%d' % i, ngettext('%d minute', '%d minutes', i) % i))
    else:
        choicelist.append('%d' % i)

config.plugins.ClearMem.timeout = ConfigSelection(default='30', choices=choicelist)
config.plugins.ClearMem.scrinfo = ConfigYesNo(default=False)
choicelist = []
for i in range(1, 11):
    if NGETTEXT:
        choicelist.append(('%d' % i, ngettext('%d second', '%d seconds', i) % i))
    else:
        choicelist.append('%d' % i)

config.plugins.ClearMem.timescrinfo = ConfigSelection(default='10', choices=choicelist)
cfg = config.plugins.ClearMem
ALL = 23

def clearMem():
    system('sync')
    system('echo 3 > /proc/sys/vm/drop_caches')


class ItalyRamPanel(Screen, ConfigListScreen):
    skin = '\n\t<screen name="ItalyRamPanel" position="center,center" size="500,215" title="" backgroundColor="#31000000" >\n\t\t<widget name="config" position="10,10" size="480,125" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />\n\t\t<widget name="memory" position="10,145" zPosition="2" size="480,24" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />\n\t\t<widget name="slide" position="10,170" zPosition="2" borderWidth="1" size="480,8" backgroundColor="dark" />\n\t\t<ePixmap pixmap="skin_default/div-h.png" position="0,183" zPosition="2" size="500,2" />\n\t\t<widget name="key_red" position="0,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />\n\t\t<widget name="key_green" position="120,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />\n\t\t<widget name="key_yellow" position="240,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="yellow" />\n\t\t<widget name="key_blue" position="360,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self.setup_title = _('Setup Clear Memory')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.keyCancel,
         'green': self.keySave,
         'ok': self.keySave,
         'red': self.keyCancel,
         'blue': self.freeMemory,
         'yellow': self.memoryInfo}, -2)
        self['key_green'] = Label(_('Save'))
        self['key_red'] = Label(_('Cancel'))
        self['key_blue'] = Label(_('Clear Now'))
        self['key_yellow'] = Label(_('Info'))
        self['slide'] = ProgressBar()
        self['slide'].setValue(100)
        self['slide'].hide()
        self['memory'] = Label()
        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_('Setup ClearMem'))
        self['memory'].setText(self.getMemory(ALL))

    def runSetup(self):
        self.list = [getConfigListEntry(_('Enable ClearMem'), cfg.enable)]
        if cfg.enable.value:
            autotext = _('Auto timeout:')
            timetext = _('Time of info message:')
            if not NGETTEXT:
                autotext = _('Auto timeout (5-150min):')
                timetext = _('Time of info message (1-10sec):')
            self.list.extend((getConfigListEntry(autotext, cfg.timeout), getConfigListEntry(_('Show info on screen:'), cfg.scrinfo), getConfigListEntry(timetext, cfg.timescrinfo)))
        self['config'].list = self.list
        self['config'].setList(self.list)

    def keySave(self):
        for x in self['config'].list:
            x[1].save()

        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        if self['config'].getCurrent()[1] == cfg.enable:
            self.runSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if self['config'].getCurrent()[1] == cfg.enable:
            self.runSetup()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def freeMemory(self):
        clearMem()
        self['memory'].setText(self.getMemory(ALL))

    def getMemory(self, par = 1):
        try:
            mm = mu = mf = 0
            for line in open('/proc/meminfo', 'r'):
                line = line.strip()
                if 'MemTotal:' in line:
                    line = line.split()
                    mm = int(line[1])
                if 'MemFree:' in line:
                    line = line.split()
                    mf = int(line[1])
                    break

            mu = mm - mf
            self['memory'].setText('')
            self['slide'].hide()
            memory = ''
            if par & 1:
                memory += ''.join((_('Memory:'),
                 ' %d ' % (mm / 1024),
                 _('MB'),
                 '  '))
            if par & 2:
                memory += ''.join((_('Used:'), ' %.2f%s' % (100.0 * mu / mm, '%'), '  '))
            if par & 4:
                memory += ''.join((_('Free:'), ' %.2f%s' % (100.0 * mf / mm, '%')))
            if par & 16:
                self['slide'].setValue(int(100.0 * mu / mm + 0.25))
                self['slide'].show()
            return memory
        except Exception as e:
            print '[ClearMem] getMemory FAIL:', e
            return ''

    def memoryInfo(self):
        from ItalysatMemory import ItalyMemoryPanel
        self.session.openWithCallback(self.afterInfo, ItalyMemoryPanel)

    def afterInfo(self, answer = False):
        self['memory'].setText(self.getMemory(ALL))


class ClearMemAutoMain:

    def __init__(self):
        self.dialog = None
        return

    def startClearMem(self, session):
        self.dialog = session.instantiateDialog(ClearMemAutoScreen)
        self.makeShow()

    def makeShow(self):
        if cfg.scrinfo.value:
            self.dialog.show()
        else:
            self.dialog.hide()


ClearMemAuto = ClearMemAutoMain()

class ClearMemAutoScreen(Screen):
    skin = '<screen name="ItalySatRamScreen" position="830,130" zPosition="10" size="250,30" title="ClearMem Status" backgroundColor="#31000000" >\n\t\t\t<widget name="message_label" font="Regular;24" position="0,0" zPosition="2" valign="center" halign="center" size="250,30" backgroundColor="#31000000" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin = ClearMemAutoScreen.skin
        self['message_label'] = Label(_('Starting'))
        self.ClearMemTimer = eTimer()
        self.ClearMemTimer.timeout.get().append(self.__makeWhatYouNeed)
        self.ClearMemWatchDog = eTimer()
        self.ClearMemWatchDog.timeout.get().append(self.__chckState)
        self.showTimer = eTimer()
        self.showTimer.timeout.get().append(self.__endShow)
        self.state = None
        self.onLayoutFinish.append(self.__chckState)
        self.onShow.append(self.__startsuspend)
        return

    def __startsuspend(self):
        self.setTitle(_('ClearMem Status'))
        if self.showTimer.isActive():
            self.showTimer.stop()
        self.showTimer.start(int(cfg.timescrinfo.value) * 1000)

    def __chckState(self):

        def subStart():
            if cfg.enable.value:
                self.state = cfg.enable.value
                self.ClearMemTimer.start(int(cfg.timeout.value) * 60000)
                self['message_label'].setText(_('Started'))
            else:
                self['message_label'].setText(_('Stopped'))
            if cfg.scrinfo.value and ClearMemAuto.dialog is not None:
                ClearMemAuto.dialog.show()
            return

        self.ClearMemWatchDog.stop()
        if self.instance and cfg.enable.value != self.state:
            if self.ClearMemTimer.isActive():
                self.ClearMemTimer.stop()
            subStart()
        self.ClearMemWatchDog.start(int(cfg.timescrinfo.value) * 1000)

    def __makeWhatYouNeed(self):
        self.ClearMemTimer.stop()
        clearMem()
        if self.instance:
            self['message_label'].setText(_('Mem cleared'))
            if cfg.scrinfo.value and ClearMemAuto.dialog is not None:
                ClearMemAuto.dialog.show()
        self.ClearMemTimer.start(int(cfg.timeout.value) * 60000)
        return

    def __endShow(self):
        self.showTimer.stop()
        ClearMemAuto.dialog.hide()