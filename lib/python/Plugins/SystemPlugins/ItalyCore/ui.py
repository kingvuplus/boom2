# Embedded file name: /usr/lib/enigma2/python/Plugins/SystemPlugins/ItalyCore/ui.py
from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER, gFont
from os import listdir, path, mkdir

class ItalyMenu(Screen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('ItalySat'))
        self.menu = args
        self.list = []
        if self.menu == 0:
            self.list.append(('backup-manager',
             _('Backup Setting Manager'),
             _('Manage your backups of your settings.'),
             None))
            self.list.append(('image-manager',
             _('Backup Image Manager'),
             _('Create and Restore complete images of the system.'),
             None))
        self['menu'] = List(self.list)
        self['key_red'] = Button(_('Cancel'))
        self['shortcuts'] = NumberActionMap(['ShortcutActions',
         'WizardActions',
         'InfobarEPGActions',
         'MenuActions',
         'NumberActions'], {'ok': self.go,
         'red': self.close,
         'back': self.close}, -1)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onChangedEntry = []
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        return

    def createSummary(self):
        from Screens.PluginBrowser import PluginBrowserSummary
        return PluginBrowserSummary

    def selectionChanged(self):
        item = self['menu'].getCurrent()
        if item:
            name = item[1]
            desc = item[2]
        else:
            name = '-'
            desc = ''
        for cb in self.onChangedEntry:
            cb(name, desc)

    def layoutFinished(self):
        idx = 0
        self['menu'].index = idx

    def setWindowTitle(self):
        self.setTitle(_('ItalySat'))

    def go(self, num = None):
        if num is not None:
            num -= 1
            if not num < self['menu'].count():
                return
            self['menu'].setIndex(num)
        current = self['menu'].getCurrent()
        if current:
            currentEntry = current[0]
            if self.menu == 0:
                if currentEntry == 'backup-manager':
                    from ItalySat.ItalysatBackupManager import ItalyBackupManager
                    self.session.open(ItalyBackupManager)
                elif currentEntry == 'image-manager':
                    from ItalySat.ItalysatImageManager import ItalyImageManager
                    self.session.open(ItalyImageManager)
        return