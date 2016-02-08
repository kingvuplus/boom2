# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatExtra.py
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console
from enigma import eTimer, loadPic, eDVBDB, eConsoleAppContainer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap, MultiPixmap
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, createDir, resolveFilename, SCOPE_PLUGINS
from os import system, remove, listdir, chdir, getcwd
from ItalysatUtils import ItalysatUtils, ItalysatGetSkinPath, italysat_strip_html
from ItalysatDownloader import ItalyDownloader
from ItalysatConsole import ItalyConsole
from Tools import Notifications
import xml.etree.cElementTree as x
t = ItalysatUtils()

class util():
    pluginIndex = -1
    pluginType = ''
    typeDownload = 'A'
    addonsName = ''
    filename = ''
    dir = ''
    size = 0
    check = 0

    def removeSetting(self):
        print 'Remove settings'
        system('rm -f /etc/enigma2/*.radio')
        system('rm -f /etc/enigma2/*.tv')
        system('rm -f /etc/enigma2/lamedb')
        system('rm -f /etc/enigma2/blacklist')
        system('rm -f /etc/enigma2/whitelist')

    def reloadSetting(self):
        print 'Reload settings'
        self.eDVBDB = eDVBDB.getInstance()
        self.eDVBDB.reloadServicelist()
        self.eDVBDB.reloadBouquets()


u = util()

class loadXml():
    tree_list = []
    plugin_list = []

    def load(self, filename):
        del self.tree_list[:]
        del self.plugin_list[:]
        tree = x.parse(filename)
        root = tree.getroot()
        c = 0
        for tag in root.getchildren():
            self.tree_list.append([c, tag.tag])
            c1 = 0
            for b in tree.find(tag.tag):
                self.plugin_list.append([c,
                 tag.tag,
                 b.find('Filename').text,
                 b.find('Descr').text,
                 b.find('Folder').text,
                 b.find('Size').text,
                 b.find('Check').text,
                 c1])
                c1 += 1

            c += 1


loadxml = loadXml()

class ItalyAddonsMenu(Screen):
    __module__ = __name__
    skin = '\n\t<screen name="Italy Addons Panel Menu" position="center,center" size="634,474" title="ItalySat Addons Panel Menu">\n\t\t<widget source="list" render="Listbox" position="12,6" size="611,424" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=2),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<widget source="conn" render="Label" position="14,434" size="608,26" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t</screen>'
    FREESPACENEEDUPGRADE = 4000
    CANUPGRADE = False

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['conn'] = StaticText('')
        self['spaceused'] = ProgressBar()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.containerExtra = eConsoleAppContainer()
        self.containerExtra.appClosed.append(self.runFinishedExtra)
        self.containerClone = eConsoleAppContainer()
        self.containerClone.appClosed.append(self.runFinishedClone)
        self.reloadTimer = eTimer()
        self.reloadTimer.timeout.get().append(self.relSetting)
        self.linkAddons = t.readAddonsPers()
        self.linkExtra = t.readExtraUrl()
        self.linkClone = t.readCloneUrl()
        isPluginManager = False
        if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SoftwareManager/plugin.pyo')):
            isPluginManager = True
        self.MenuList = [('ItalyAddonsManager',
          _('Download Addons'),
          'italy_icons/gre_network.png',
          True),
         ('ItalyRemAddons',
          _('Remove Addons Installed'),
          'italy_icons/gre_remove.png',
          True),
         ('ItalyPersDow',
          _('Download Personal Addons'),
          'italy_icons/gre_network.png',
          fileExists('/etc/it_personal.url')),
         ('ItalyExtraDow',
          _('Download Extra Addons'),
          'italy_icons/gre_network.png',
          fileExists('/etc/it_extra.url')),
         ('ItalyExtraDow2',
          _('Download Extra Addons 2'),
          'italy_icons/gre_network.png',
          fileExists('/etc/it_extra2.url')),
         ('ItalyDreamboxClone',
          _('Download Dreambox Driver Clone'),
          'italy_icons/gre_network.png',
          fileExists('/etc/dream')),
         ('ItalyManInstall',
          _('Manual Package Install'),
          'italy_icons/gre_manual.png',
          True),
         ('ItalyRelSettings',
          _('Reload Channell Settings'),
          'italy_icons/gre_enigma.png',
          True),
         ('ItalyCrossepg',
          _('Remove Crossepg Cache'),
          'italy_icons/gre_enigma.png',
          True)]
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.cancel,
         'back': self.cancel})
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    def ConvertSize(self, size):
        size = int(size)
        if size >= 1073741824:
            Size = '%0.2f TB' % (size / 1073741824.0)
        elif size >= 1048576:
            Size = '%0.2f GB' % (size / 1048576.0)
        elif size >= 1024:
            Size = '%0.2f MB' % (size / 1024.0)
        else:
            Size = '%0.2f KB' % size
        return str(Size)

    def setWindowTitle(self):
        diskSpace = t.getVarSpaceKb()
        percFree = int(diskSpace[0] / diskSpace[1] * 100)
        percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
        self.setTitle('%s - %s: %s (%d%%)' % (_('ItalySat Addons'),
         _('Free'),
         self.ConvertSize(int(diskSpace[0])),
         percFree))
        self['spaceused'].setValue(percUsed)

    def KeyOk(self):
        self['conn'].text = ''
        if not self.container.running():
            sel = self['list'].getCurrent()[0]
            if sel == 'ItalyAddonsManager':
                from Screens.PluginBrowser import PluginDownloadBrowser
                self.session.open(PluginDownloadBrowser, PluginDownloadBrowser.DOWNLOAD)
            elif sel == 'ItalyRemAddons':
                from Screens.PluginBrowser import PluginDownloadBrowser
                self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.REMOVE)
            elif sel == 'ItalyPersDow':
                self['conn'].text = _('Connetting to addons server.\nPlease wait...')
                u.typeDownload = 'A'
                if self.linkAddons != None:
                    self.container.execute('wget ' + self.linkAddons + 'addons.xml -O /tmp/addons.xml')
                    print self.linkAddons + 'addons.xml'
                else:
                    self['conn'].text = _('Server not found!\nPlease check internet connection.')
            elif sel == 'ItalyExtraDow':
                self['conn'].text = _('Connetting to addons server.\nPlease wait...')
                u.typeDownload = 'E'
                if self.linkExtra != None:
                    self.containerExtra.execute('wget ' + self.linkExtra + 'fydtebakfhtirpdhrq/tmp.tmp -O /tmp/tmp.tmp')
                else:
                    self['conn'].text = _('Server not found!\nPlease check internet connection.')
            elif sel == 'ItalyExtraDow2':
                self['conn'].text = _('Connetting to addons server.\nPlease wait...')
                u.typeDownload = 'E'
                if self.linkExtra != None:
                    self.containerExtra.execute('wget ' + self.linkExtra + 'fydtebakfhtirpdhrq/tmp.tmp -O /tmp/tmp.tmp')
                else:
                    self['conn'].text = _('Server not found!\nPlease check internet connection.')
            elif sel == 'ItalyDreamboxClone':
                self['conn'].text = _('Connetting to addons server.\nPlease wait...')
                u.typeDownload = 'G'
                if self.linkClone != None:
                    self.containerClone.execute('wget ' + self.linkClone + 'addons.xml -O /tmp/addons.xml')
                else:
                    self['conn'].text = _('Server not found!\nPlease check internet connection.')
            elif sel == 'ItalyManInstall':
                from ItalysatIPKInstaller import ItalyIPKInstaller
                self.session.open(ItalyIPKInstaller)
            elif sel == 'ItalySoftUpdate':
                if not self.CANUPGRADE and not fileExists('/etc/.testmode'):
                    msg = _('No Upgrade available!\nYour decoder is up to date.')
                    self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                    return
                if int(t.getVarSpaceKb()[0]) < self.FREESPACENEEDUPGRADE:
                    msg = _('Not enough free space on flash to perform Upgrade!\nUpgrade require at least %d kB free on Flash.\nPlease remove some addons or skins before upgrade.') % self.FREESPACENEEDUPGRADE
                    self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                    return
                self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to update your Box?') + '\n' + _('\nAfter pressing OK, please wait!'))
            elif sel == 'ItalyRelSettings':
                self['conn'].text = _('Reload settings, please wait...')
                self.reloadTimer.start(250, True)
            elif sel == 'ItalyCrossepg':
                self['conn'].text = _('Removing Cache CrossEPG, please wait...')
                from enigma import eEPGCache
                epgcache = eEPGCache.getInstance()
                epgcache.save()
                if fileExists('/etc/enigma2/epg.dat'):
                    remove('/etc/enigma2/epg.dat')
                if fileExists('/media/usb/crossepg'):
                    system('rm -R /media/usb/crossepg')
                if fileExists('/media/usb1/crossepg'):
                    system('rm -R /media/usb1/crossepg')
                if fileExists('/media/usb1/crossepg'):
                    system('rm -R /media/usb1/crossepg')
                if fileExists('/media/usb2/crossepg'):
                    system('rm -R /media/usb2/crossepg')
                if fileExists('/media/usb3/crossepg'):
                    system('rm -R /media/usb3/crossepg')
                if fileExists('/media/usb4/crossepg'):
                    system('rm -R /media/usb4/crossepg')
                if fileExists('/media/hdd/crossepg'):
                    system('rm -R /media/hdd/crossepg')
                if fileExists('/media/hdd1/crossepg'):
                    system('rm -R /media/hdd1/crossepg')
                if fileExists('/media/hdd2/crossepg'):
                    system('rm -R /media/hdd2/crossepg')
                if fileExists('/media/sda1/crossepg'):
                    system('rm -R /media/sda1/crossepg')
                if fileExists('/media/sda2/crossepg'):
                    system('rm -R /media/sda2/crossepg')
                if fileExists('/media/sdb1/crossepg'):
                    system('rm -R /media/sdb1/crossepg')
                if fileExists('/media/sdb2/crossepg'):
                    system('rm -R /media/sdb2/crossepg')
                if fileExists('/media/sdc1/crossepg'):
                    system('rm -R /media/sdc1/crossepg')
                if fileExists('/media/sdc2/crossepg'):
                    system('rm -R /media/sdc2/crossepg')
                if fileExists('/media/sdd1/crossepg'):
                    system('rm -R /media/sdd1/crossepg')
                if fileExists('/media/sdd2/crossepg'):
                    system('rm -R /media/sdd2/crossepg')
                system('/usr/crossepg/crossepg_epgmove.sh')
                self['conn'].text = _('Cache CrossEPG Removed\nPlease re-downloads EPG')
        return

    def StatsDone(self):
        downfile = '/tmp/itapan.tmp'
        if fileExists(downfile):
            self.session.open(ItalySatStatistic)
        else:
            nobox = self.session.open(MessageBox, _('Sorry, Connection Failed.'), MessageBox.TYPE_INFO)

    def relSetting(self):
        u.reloadSetting()
        self['conn'].text = _('Settings reloaded succesfully!')

    def runUpgrade(self, result):
        if result:
            try:
                from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
            except ImportError:
                self.session.open(MessageBox, _('The Softwaremanagement extension is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
            else:
                self.session.open(UpdatePlugin, ItalysatGetSkinPath())

    def runFinished(self, retval):
        if fileExists('/tmp/addons.xml'):
            try:
                loadxml.load('/tmp/addons.xml')
                remove('/tmp/addons.xml')
                self['conn'].text = ''
                self.session.open(ItalyExtraList)
            except:
                self['conn'].text = _('File xml is not correctly formatted!')

        else:
            self['conn'].text = _('Server not found!\nPlease check internet connection.')

    def runFinishedExtra(self, retval):
        if fileExists('/tmp/tmp.tmp'):
            try:
                f = open('/tmp/tmp.tmp', 'r')
                line = f.readline()[:-1]
                f.close()
                self.container.execute('wget ' + self.linkExtra + 'fydtebakfhtirpdhrq/' + line + ' -O /tmp/addons.xml')
            except:
                self['conn'].text = _('Server not found!\nPlease check internet connection.')

        else:
            self['conn'].text = _('Server not found!\nPlease check internet connection.')

    def runFinishedClone(self, retval):
        if fileExists('/tmp/addons.xml'):
            try:
                loadxml.load('/tmp/addons.xml')
                remove('/tmp/addons.xml')
                self['conn'].text = ''
                self.session.open(ItalyExtraList)
            except:
                self['conn'].text = _('File xml is not correctly formatted!')

        else:
            self['conn'].text = _('Server not found!\nPlease check internet connection.')

    def cancel(self):
        if not self.container.running() and not self.containerExtra.running():
            del self.container.appClosed[:]
            del self.container
            del self.containerExtra.appClosed[:]
            del self.containerExtra
            del self.containerClone.appClosed[:]
            del self.containerClone
            self.close()
        else:
            if self.container.running():
                self.container.kill()
            if self.containerExtra.running():
                self.containerExtra.kill()
            if self.containerClone.running():
                self.containerClone.kill()
            if fileExists('/tmp/addons.xml'):
                remove('/tmp/addons.xml')
            if fileExists('/tmp/tmp.tmp'):
                remove('/tmp/tmp.tmp')
            self['conn'].text = _('Process Killed by user\nServer Not Connected!')

    def updateList(self):
        del self.list[:]
        skin_path = ItalysatGetSkinPath()
        for i in self.MenuList:
            if i[3]:
                self.list.append((i[0], i[1], LoadPixmap(skin_path + i[2])))

        self['list'].setList(self.list)

    def PluginDownloadBrowserClosed(self):
        self.updateList()


class ItalyExtraList(Screen):
    __module__ = __name__
    skin = '\n\t<screen name="Italy Extra Downloads" position="center,center" size="634,474" title="ItalySat Extra Downloads">\n\t\t<widget source="list" render="Listbox" position="12,6" size="611,386" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (5, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 36\n\t\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t  <ePixmap position="115,419" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="on" />\n\t  <ePixmap position="414,416" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" />\n\t  <widget name="key_red" position="112,418" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t  <widget name="key_green" position="416,417" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" /> \n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Continue'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'back': self.close,
         'red': self.close,
         'green': self.KeyOk})
        self.onLayoutFinish.append(self.loadData)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(self.title)

    def KeyOk(self):
        u.pluginType = self['list'].getCurrent()[0]
        u.pluginIndex = self['list'].getIndex()
        self.session.open(ItalyExtraDown)

    def loadData(self):
        del self.list[:]
        for tag in loadxml.tree_list:
            self.list.append((tag[1], tag[1]))

        self['list'].setList(self.list)


class ItalyExtraDown(Screen):
    __module__ = __name__
    skin = '\n\t<screen name="Italy Extra Download" position="center,center" size="560,530" title="ItalySat Extra Downloader">\n\t\t<widget source="list" render="Listbox" position="17,6" size="540,416" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\t\tMultiContentEntryText(pos = (5, 0), size = (530, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<widget source="conn" render="Label" position="16,425" size="540,55" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="210,491" size="140,40" alphatest="on" />\n\t  <widget name="key_red" position="112,418" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t  <widget name="key_green" position="416,417" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" /> \n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['conn'] = StaticText(_('Loading elements.\nPlease wait...'))
        self['type'] = Label('')
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Continue'))
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self['type'].setText(_('Download ') + str(u.pluginType))
        self.linkAddons = t.readAddonsPers()
        self.linkExtra = t.readExtraUrl()
        self.linkClone = t.readCloneUrl()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'back': self.cancel,
         'red': self.cancel,
         'green': self.KeyOk})
        self.onLayoutFinish.append(self.loadPlugin)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('ItalySat Download ') + str(u.pluginType))

    def KeyOk(self):
        if not self.container.running():
            self.sel = self['list'].getIndex()
            for tag in loadxml.plugin_list:
                if tag[0] == u.pluginIndex:
                    if tag[7] == self.sel:
                        u.addonsName = tag[3]
                        self.downloadAddons()
                        return

            self.close()

    def loadPlugin(self):
        del self.list[:]
        for tag in loadxml.plugin_list:
            if tag[0] == u.pluginIndex:
                self.list.append((tag[3], tag[3]))

        self['list'].setList(self.list)
        self['conn'].text = _('Elements Loaded!. Please select one to install.')

    def downloadAddons(self):
        self.getAddonsPar()
        if int(u.size) > int(t.getVarSpaceKb()[0]) and int(u.check) != 0:
            msg = _('Not enough space!\nPlease delete addons before install new.')
            self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
            return
        url = {'E': self.linkExtra,
         'A': self.linkAddons,
         'G': self.linkClone}[u.typeDownload] + u.dir + '/' + u.filename
        self.session.openWithCallback(self.executedScript, ItalyDownloader, url, '/tmp/', u.filename)

    def executedScript(self, *answer):
        if answer[0] == ItalyConsole.EVENT_DONE:
            if fileExists('/tmp/' + u.filename):
                msg = _('Do you want install the addon:\n%s?') % u.addonsName
                box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Install Addon'))
            else:
                msg = _('File: %s not found!\nPlease check your internet connection.') % u.filename
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
        elif answer[0] == ItalyConsole.EVENT_KILLED:
            self['conn'].text = _('Process Killed by user!\nAddon not downloaded.')

    def installAddons(self, answer):
        if answer is True:
            if u.filename.find('.ipk') != -1:
                dest = '/tmp/' + u.filename
                mydir = getcwd()
                chdir('/')
                cmd = 'opkg install ' + '--force-overwrite ' + dest
                cmd2 = 'rm -f ' + dest
                self.session.open(Console, title=_('Ipk Package Installation'), cmdlist=[cmd, cmd2], finishedCallback=self.runFinishedIPK)
                chdir(mydir)
                self['conn'].text = _('Addon installed succesfully!')
            elif u.filename.find('.tbz') != -1:
                self.container.execute('tar -xjvf /tmp/' + u.filename + ' -C /')
                self['conn'].text = _('Please wait..Installing!')
            elif u.filename.find('.tar.gz') != -1:
                self.container.execute('tar -xzvf /tmp/' + u.filename + ' -C /')
                self['conn'].text = _('Please wait..Installing!')
            elif u.filename.find('.tgz') != -1:
                self.container.execute('tar -xzvf /tmp/' + u.filename + ' -C /')
                self['conn'].text = _('Please wait..Installing!')
            else:
                self['conn'].text = _('File: %s\nis not a valid package!') % u.filename
        elif fileExists('/tmp/' + u.filename):
            remove('/tmp/' + u.filename)

    def runFinishedIPK(self):
        if u.typeDownload == 'G':
            self['conn'].text = _('Addon installed succesfully!')
            msg = _('Box will be now hard rebooted to complete package installation.') + '\n' + _('Do you want reboot now?')
            box = self.session.openWithCallback(self.restartBox, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle(_('Reboot'))

    def runFinished(self, retval):
        if fileExists('/tmp/' + u.filename):
            remove('/tmp/' + u.filename)
        if u.pluginType == 'Plugins' or u.pluginType == 'Plugin':
            self['conn'].text = _('Reload Plugins list\nPlease Wait...')
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self['conn'].text = _('Addon installed succesfully!')
            msg = _('Enigma2 will be now hard restarted to complete package installation.') + '\n' + _('Do you want restart enigma2 now?')
            box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle(_('Restart Enigma2'))
        else:
            self['conn'].text = _('Addon installed succesfully!')

    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['conn'].text = _('Process Killed by user.\nAddon not installed correctly!')

    def restartEnigma2(self, answer):
        if answer is True:
            system('killall -9 enigma2')

    def restartBox(self, answer):
        if answer is True:
            system('reboot')

    def getAddonsPar(self):
        for tag in loadxml.plugin_list:
            if tag[0] == u.pluginIndex:
                if tag[3] == u.addonsName:
                    u.filename = tag[2]
                    u.dir = tag[4]
                    u.size = tag[5]
                    u.check = tag[6]