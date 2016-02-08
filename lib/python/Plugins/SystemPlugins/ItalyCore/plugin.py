# Embedded file name: /usr/lib/enigma2/python/Plugins/SystemPlugins/ItalyCore/plugin.py
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigBoolean
from Components.Harddisk import harddiskmanager
from ItalySat.ItalysatBackupManager import BackupManagerautostart
from ItalySat.ItalysatImageManager import ImageManagerautostart
from ItalySat.ItalysatSwapManager import SwapAutostart
from ItalySat.ItalysatIPKInstaller import IpkgInstaller
from os import path, listdir

def checkConfigBackup():
    try:
        devices = [ (r.description, r.mountpoint) for r in harddiskmanager.getMountedPartitions(onlyhotplug=False) ]
        list = []
        files = []
        for x in devices:
            if x[1] == '/':
                devices.remove(x)

        if len(devices):
            for x in devices:
                devpath = path.join(x[1], 'backup')
                if path.exists(devpath):
                    try:
                        files = listdir(devpath)
                    except:
                        files = []

                else:
                    files = []
                if len(files):
                    for file in files:
                        if file.endswith('.tar.gz'):
                            list.append((path.join(devpath, file), devpath, file))

        if len(list):
            return True
        return None
    except IOError as e:
        print 'unable to use device (%s)...' % str(e)
        return None

    return None


if checkConfigBackup() is None:
    backupAvailable = 0
else:
    backupAvailable = 1

def ItalyMenu(session):
    import ui
    return ui.ItalyMenu(session)


def UpgradeMain(session, **kwargs):
    session.open(ItalyMenu)


def startSetup(menuid):
    if menuid != 'setup':
        return []
    return [(_('ItalySat'),
      UpgradeMain,
      'italysat_menu',
      1010)]


config.misc.restorewizardrun = ConfigBoolean(default=False)

def ItalyRestoreWizard(*args, **kwargs):
    from ItalySat.ItalysatRestoreWizard import ItalyRestoreWizard
    return ItalyRestoreWizard(*args, **kwargs)


def ItalyBackupManager(session):
    from ItalySat.ItalysatBackupManager import ItalyBackupManager
    return ItalyBackupManager(session)


def BackupManagerMenu(session, **kwargs):
    session.open(ItalyBackupManager)


def ItalyImageManager(session):
    from ItalySat.ItalysatImageManager import ItalyImageManager
    return ItalyImageManager(session)


def ImageMangerMenu(session, **kwargs):
    session.open(ItalyImageManager)


def filescan_open(list, session, **kwargs):
    filelist = [ x.path for x in list ]
    session.open(IpkgInstaller, filelist)


def filescan(**kwargs):
    from Components.Scanner import Scanner, ScanPath
    return Scanner(mimetypes=['application/x-debian-package'], paths_to_scan=[ScanPath(path='ipk', with_subdirs=True), ScanPath(path='', with_subdirs=False)], name='Ipkg', description=_('Install extensions.'), openfnc=filescan_open)


def ItalyRam(reason, **kwargs):
    from ItalySat.ItalysatRam import ClearMemAuto
    if reason == 0:
        ClearMemAuto.startClearMem(kwargs['session'])


def Plugins(path, **kwargs):
    plist = [PluginDescriptor(where=PluginDescriptor.WHERE_ITALYMENU, needsRestart=False, fnc=startSetup)]
    plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=SwapAutostart))
    plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=ImageManagerautostart))
    plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=BackupManagerautostart))
    plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=ItalyRam))
    if config.misc.firstrun.value and not config.misc.restorewizardrun.value and backupAvailable == 1:
        plist.append(PluginDescriptor(name=_('Restore Wizard'), where=PluginDescriptor.WHERE_WIZARD, needsRestart=False, fnc=(3, ItalyRestoreWizard)))
    plist.append(PluginDescriptor(name=_('Ipkg'), where=PluginDescriptor.WHERE_FILESCAN, needsRestart=False, fnc=filescan))
    return plist