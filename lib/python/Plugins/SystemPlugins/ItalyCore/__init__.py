# Embedded file name: /usr/lib/enigma2/python/Plugins/SystemPlugins/ItalyCore/__init__.py
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, gettext
PluginLanguageDomain = 'italysat'
PluginLanguagePath = 'SystemPlugins/ItalyCore/locale'

def localeInit():
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        print '[' + PluginLanguageDomain + '] fallback to default translation for ' + txt
        return gettext.gettext(txt)


language.addCallback(localeInit())