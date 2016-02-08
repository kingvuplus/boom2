# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatSkinDev.py
from Screens.Screen import Screen

class SkinDeveloperSummary(Screen):
    skin = '\n\t<screen position="0,0" size="132,64">\n\t\t<widget source="parent.DeveloperTag" render="Label" position="6,4" size="120,42" font="Regular;18" />\n\t</screen>'

    def __init__(self, session, parent):
        Screen.__init__(self, session, parent=parent)
        names = parent.skinName
        if not isinstance(names, list):
            names = [names]
        self.skinName = [ x + '_summary' for x in names ]
        self.skinName.append('SkinDeveloperSummary')
        self.skin = parent.__dict__.get('skin_summary', self.skin)

    def updateProgress(self, value):
        pass

    def updateService(self, name):
        pass