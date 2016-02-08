# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatGreen.py
from Screens.Screen import Screen
from enigma import eTimer, eConsoleAppContainer
from boxbranding import getImageBuild, getImageVersion, getBoxType
from Components.About import about
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigText, configfile
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE, fileExists
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from ItalysatUtils import ItalysatUtils, ItalysatGetSkinPath
from os import unlink
t = ItalysatUtils()

class ItalyGreen(Screen):
    skin = '\n\t<screen name="ItalyGreen" position="center,center" size="1017,549" title="ItalySat Green Panel">\n\t\t  <widget source="list" render="Listbox" position="16,3" scrollbarMode="showOnDemand" size="989,429">\n\t\t    <convert type="TemplatedMultiContent">\n\t\t          {"template": [\n\t\t          MultiContentEntryText(pos = (125, 0), size = (650, 24), font=0, text = 0),\n\t\t          MultiContentEntryText(pos = (125, 24), size = (650, 24), font=1, text = 1),\n\t\t          MultiContentEntryPixmapAlphaTest(pos = (6, 5), size = (100, 40), png = 2),\n\t\t          ],\n\t\t          "fonts": [gFont("Regular", 24),gFont("Regular", 20)],\n\t\t          "itemHeight": 52\n\t\t          }\n\t\t      </convert>\n\t\t  </widget>\n\t\t  <widget name="conn" position="17,465" size="983,40" font="Regular;20" halign="center" valign="center" zPosition="2" foregroundColor="red" />\n\t\t  <ePixmap alphatest="blend" pixmap="skin_default/buttons/red.png" position="44,507" size="140,40" />\n\t\t  <ePixmap alphatest="blend" pixmap="skin_default/buttons/green.png" position="330,506" size="140,40" />\n\t\t  <ePixmap alphatest="blend" pixmap="skin_default/buttons/yellow.png" position="567,507" size="140,40" />\n\t\t  <ePixmap alphatest="blend" pixmap="skin_default/buttons/blue.png" position="815,509" size="140,40" />\n\t\t  <widget name="key_red" font="Regular;22" halign="left" position="44,508" size="204,40" transparent="1" zPosition="1" />\n\t\t  <widget name="key_green" font="Regular;22" halign="left" position="330,508" size="140,40" transparent="1" zPosition="1" />\n\t\t  <widget name="key_yellow" font="Regular;22" halign="left" position="567,508" size="179,40" transparent="1" zPosition="1" />\n\t\t  <widget name="key_blue" font="Regular;22" halign="left" position="815,508" size="140,40" transparent="1" zPosition="1" />\n\t</screen>'
    ITALYSATVER = getImageVersion()
    SVNVERSION = getImageBuild()

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['conn'] = Label('')
        self['conn'].hide()
        self['key_red'] = Label(_('Addons Online'))
        self['key_green'] = Label(_('Fast Plugin'))
        self['key_yellow'] = Label(_('Script Manager'))
        self['key_blue'] = Label(_('Memory Info'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'NumberActions'], {'ok': self.save,
         'back': self.close,
         'red': self.keyred,
         'green': self.keygreen,
         'yellow': self.keyyellow,
         'blue': self.keyblue,
         '5': self.ExtraUrl,
         '6': self.Plugin}, -1)
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    def Plugin(self):
        from Tools.Directories import resolveFilename, SCOPE_PLUGINS
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

    def setWindowTitle(self):
        self.setTitle('%s - %s: %s - SVN: (%s)' % (_('ItalySat'),
         _('Image Version'),
         self.ITALYSATVER,
         self.SVNVERSION))

    def save(self):
        self.run()

    def run(self):
        mysel = self['list'].getCurrent()
        if mysel:
            plugin = mysel[3]
            plugin(session=self.session)

    def updateList(self):
        self.list = []
        self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
        for plugin in self.pluginlist:
            if plugin.icon is None:
                png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/icons/plugin.png'))
            else:
                png = plugin.icon
            res = (plugin.name,
             plugin.description,
             png,
             plugin)
            self.list.append(res)

        self['list'].list = self.list
        return

    def keyred(self):
        from ItalysatExtra import ItalyAddonsMenu
        self.session.open(ItalyAddonsMenu)

    def keyyellow(self):
        from ItalysatScript import ItalyScriptPanel
        self.session.open(ItalyScriptPanel)

    def keyblue(self):
        from ItalysatMemory import ItalyMemoryPanel
        self.session.open(ItalyMemoryPanel)

    def keygreen(self):
        result = ''
        check = False
        myplug = config.italysat.fp.value
        for plugin in self.list:
            result = plugin[3].name
            if result == myplug:
                runplug = plugin[3]
                check = True
                break

        if check == True:
            runplug(session=self.session)
        else:
            mybox = self.session.open(MessageBox, _('Setup Fast Plugin before to use this button.'), MessageBox.TYPE_INFO)
            mybox.setTitle(_('Info'))

    def NotYet(self):
        mybox = self.session.open(MessageBox, _('Function Not Yet Available'), MessageBox.TYPE_INFO)
        mybox.setTitle(_('Info'))

    def ExtraUrl(self):
        if fileExists('/etc/it_extra.url') or fileExists('/etc/it_extra2.url'):
            print 'Ok'
        else:
            extra = open('/etc/it_extra.url', 'w')
            line = 'http://www.italysat.allalla.com/'
            extra.write(line + '\n')
            extra.close()
            extra = open('/etc/it_extra2.url', 'w')
            line = 'http://italysat.altervista.org/'
            extra.write(line + '\n')
            extra.close()


class ItalyGreenPanel:

    def __init__(self):
        self['ItalyGreenPanel'] = ActionMap(['InfobarSubserviceSelectionActions'], {'ItalyGreenPanelshow': self.showItalyGreenPanel})

    def showItalyGreenPanel(self):
        self.session.openWithCallback(self.callItalyAction, ItalyGreen)

    def callItalyAction(self, *args):
        if len(args):
            actionmap, context, action = args
            actionmap.action(context, action)