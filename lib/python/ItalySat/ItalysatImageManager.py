# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatImageManager.py
from boxbranding import getBoxType, getImageDistro, getImageVersion, getImageBuild, getImageFolder, getImageFileSystem, getBrandOEM, getMachineBrand, getMachineName, getMachineBuild, getMachineMake, getMachineMtdRoot, getMachineRootFile, getMachineMtdKernel, getMachineKernelFile, getMachineMKUBIFS, getMachineUBINIZE
from os import path, system, mkdir, makedirs, listdir, remove, statvfs, chmod, walk, symlink, unlink
from shutil import rmtree, move, copy
from time import localtime, time, strftime, mktime
from enigma import eTimer
import Components.Task
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Button import Button
from Components.MenuList import MenuList
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigText, ConfigNumber, NoSave, ConfigClock
from Components.Harddisk import harddiskmanager, getProcMounts
from Screens.Screen import Screen
from Screens.Setup import Setup
from Components.Console import Console
from Screens.Console import Console as ScreenConsole
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Tools.Notifications import AddPopupWithCallback
import urllib
from os import rename, path, remove
RAMCHEKFAILEDID = 'RamCheckFailedNotification'
hddchoises = []
for p in harddiskmanager.getMountedPartitions():
    if path.exists(p.mountpoint):
        d = path.normpath(p.mountpoint)
        if p.mountpoint != '/':
            hddchoises.append((p.mountpoint, d))

config.imagemanager = ConfigSubsection()
config.imagemanager.folderprefix = ConfigText(default=getImageDistro() + '-' + getBoxType(), fixed_size=False)
config.imagemanager.backuplocation = ConfigSelection(choices=hddchoises)
config.imagemanager.schedule = ConfigYesNo(default=False)
config.imagemanager.scheduletime = ConfigClock(default=0)
config.imagemanager.repeattype = ConfigSelection(default='daily', choices=[('daily', _('Daily')), ('weekly', _('Weekly')), ('monthly', _('30 Days'))])
config.imagemanager.backupretry = ConfigNumber(default=30)
config.imagemanager.backupretrycount = NoSave(ConfigNumber(default=0))
config.imagemanager.nextscheduletime = NoSave(ConfigNumber(default=0))
config.imagemanager.restoreimage = NoSave(ConfigText(default=getBoxType(), fixed_size=False))
autoImageManagerTimer = None
if path.exists(config.imagemanager.backuplocation.value + 'imagebackups/imagerestore'):
    try:
        rmtree(config.imagemanager.backuplocation.value + 'imagebackups/imagerestore')
    except:
        pass

def ImageManagerautostart(reason, session = None, **kwargs):
    global autoImageManagerTimer
    global _session
    now = int(time())
    if reason == 0:
        print '[ImageManager] AutoStart Enabled'
        if session is not None:
            _session = session
            if autoImageManagerTimer is None:
                autoImageManagerTimer = AutoImageManagerTimer(session)
    elif autoImageManagerTimer is not None:
        print '[ImageManager] Stop'
        autoImageManagerTimer.stop()
    return


class ItalyImageManager(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Image Manager'))
        self['lab1'] = Label()
        self['backupstatus'] = Label()
        self['key_blue'] = Button(_('Restore'))
        self['key_green'] = Button()
        self['key_yellow'] = Button(_('Downloads'))
        self['key_red'] = Button(_('Delete'))
        self.BackupRunning = False
        self.onChangedEntry = []
        self.oldlist = None
        self.emlist = []
        self['list'] = MenuList(self.emlist)
        self.populate_List()
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.backupRunning)
        self.activityTimer.start(10)
        self.Console = Console()
        if BackupTime > 0:
            t = localtime(BackupTime)
            backuptext = _('Next Backup: ') + strftime(_('%a %e %b  %-H:%M'), t)
        else:
            backuptext = _('Next Backup: ')
        self['backupstatus'].setText(str(backuptext))
        if self.selectionChanged not in self['list'].onSelectionChanged:
            self['list'].onSelectionChanged.append(self.selectionChanged)
        return

    def createSummary(self):
        from Screens.PluginBrowser import PluginBrowserSummary
        return PluginBrowserSummary

    def selectionChanged(self):
        item = self['list'].getCurrent()
        desc = self['backupstatus'].text
        if item:
            name = item
        else:
            name = ''
        for cb in self.onChangedEntry:
            cb(name, desc)

    def backupRunning(self):
        self.populate_List()
        self.BackupRunning = False
        for job in Components.Task.job_manager.getPendingJobs():
            if job.name.startswith(_('Image Manager')):
                self.BackupRunning = True

        if self.BackupRunning:
            self['key_green'].setText(_('View Progress'))
        else:
            self['key_green'].setText(_('New Backup'))
        self.activityTimer.startLongTimer(5)

    def refreshUp(self):
        self.refreshList()
        if self['list'].getCurrent():
            self['list'].instance.moveSelection(self['list'].instance.moveUp)

    def refreshDown(self):
        self.refreshList()
        if self['list'].getCurrent():
            self['list'].instance.moveSelection(self['list'].instance.moveDown)

    def refreshList(self):
        images = listdir(self.BackupDirectory)
        self.oldlist = images
        del self.emlist[:]
        for fil in images:
            if fil.endswith('.zip') or path.isdir(path.join(self.BackupDirectory, fil)):
                self.emlist.append(fil)

        self.emlist.sort()
        self.emlist.reverse()
        self['list'].setList(self.emlist)
        self['list'].show()

    def getJobName(self, job):
        return '%s: %s (%d%%)' % (job.getStatustext(), job.name, int(100 * job.progress / float(job.end)))

    def showJobView(self, job):
        from Screens.TaskView import JobView
        Components.Task.job_manager.in_background = False
        self.session.openWithCallback(self.JobViewCB, JobView, job, cancelable=False, backgroundable=False, afterEventChangeable=False, afterEvent='close')

    def JobViewCB(self, in_background):
        Components.Task.job_manager.in_background = in_background

    def populate_List(self):
        imparts = []
        for p in harddiskmanager.getMountedPartitions():
            if path.exists(p.mountpoint):
                d = path.normpath(p.mountpoint)
                if p.mountpoint != '/':
                    imparts.append((p.mountpoint, d))

        config.imagemanager.backuplocation.setChoices(imparts)
        if config.imagemanager.backuplocation.value.endswith('/'):
            mount = (config.imagemanager.backuplocation.value, config.imagemanager.backuplocation.value[:-1])
        else:
            mount = (config.imagemanager.backuplocation.value + '/', config.imagemanager.backuplocation.value)
        hdd = ('/media/hdd/', '/media/hdd')
        if mount not in config.imagemanager.backuplocation.choices.choices:
            if hdd in config.imagemanager.backuplocation.choices.choices:
                self['myactions'] = ActionMap(['ColorActions',
                 'OkCancelActions',
                 'DirectionActions',
                 'MenuActions',
                 'HelpActions'], {'ok': self.keyResstore,
                 'cancel': self.close,
                 'red': self.keyDelete,
                 'green': self.GreenPressed,
                 'blue': self.keyResstore,
                 'menu': self.createSetup,
                 'up': self.refreshUp,
                 'down': self.refreshDown}, -1)
                self.BackupDirectory = '/media/hdd/imagebackups/'
                config.imagemanager.backuplocation.value = '/media/hdd/'
                config.imagemanager.backuplocation.save()
                self['lab1'].setText(_('The chosen location does not exist, using /media/hdd') + '\n' + _('Select an image to restore:'))
            else:
                self['myactions'] = ActionMap(['ColorActions',
                 'OkCancelActions',
                 'DirectionActions',
                 'MenuActions'], {'cancel': self.close,
                 'menu': self.createSetup}, -1)
                self['lab1'].setText(_('Device: None available') + '\n' + _('Select an image to restore:'))
        else:
            self['myactions'] = ActionMap(['ColorActions',
             'OkCancelActions',
             'DirectionActions',
             'MenuActions',
             'HelpActions'], {'cancel': self.close,
             'red': self.keyDelete,
             'green': self.GreenPressed,
             'blue': self.keyResstore,
             'menu': self.createSetup,
             'up': self.refreshUp,
             'down': self.refreshDown,
             'ok': self.keyResstore}, -1)
            self.BackupDirectory = config.imagemanager.backuplocation.value + 'imagebackups/'
            s = statvfs(config.imagemanager.backuplocation.value)
            free = s.f_bsize * s.f_bavail / 1048576
            self['lab1'].setText(_('Device: ') + config.imagemanager.backuplocation.value + ' ' + _('Free space:') + ' ' + str(free) + _('MB') + '\n' + _('Select an image to restore:'))
        try:
            if not path.exists(self.BackupDirectory):
                mkdir(self.BackupDirectory, 493)
            if path.exists(self.BackupDirectory + config.imagemanager.folderprefix.value + '-swapfile_backup'):
                system('swapoff ' + self.BackupDirectory + config.imagemanager.folderprefix.value + '-swapfile_backup')
                remove(self.BackupDirectory + config.imagemanager.folderprefix.value + '-swapfile_backup')
            self.refreshList()
        except:
            self['lab1'].setText(_('Device: ') + config.imagemanager.backuplocation.value + '\n' + _('there is a problem with this device, please reformat and try again.'))

    def createSetup(self):
        self.session.openWithCallback(self.setupDone, Setup, 'italyimagemanager', 'SystemPlugins/ItalyCore')

    def doDownload(self):
        self.session.openWithCallback(self.populate_List, ImageManagerDownload, self.BackupDirectory)

    def setupDone(self, test = None):
        self.populate_List()
        self.doneConfiguring()

    def doneConfiguring(self):
        global BackupTime
        now = int(time())
        if config.imagemanager.schedule.value:
            if autoImageManagerTimer is not None:
                print '[ImageManager] Backup Schedule Enabled at', strftime('%c', localtime(now))
                autoImageManagerTimer.backupupdate()
        elif autoImageManagerTimer is not None:
            BackupTime = 0
            print '[ImageManager] Backup Schedule Disabled at', strftime('%c', localtime(now))
            autoImageManagerTimer.backupstop()
        if BackupTime > 0:
            t = localtime(BackupTime)
            backuptext = _('Next Backup: ') + strftime(_('%a %e %b  %-H:%M'), t)
        else:
            backuptext = _('Next Backup: ')
        self['backupstatus'].setText(str(backuptext))
        return

    def keyDelete(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            message = _('Are you sure you want to delete this backup:\n ') + self.sel
            ybox = self.session.openWithCallback(self.doDelete, MessageBox, message, MessageBox.TYPE_YESNO, default=False)
            ybox.setTitle(_('Remove Confirmation'))
        else:
            self.session.open(MessageBox, _('You have no image to delete.'), MessageBox.TYPE_INFO, timeout=10)

    def doDelete(self, answer):
        if answer is True:
            self.sel = self['list'].getCurrent()
            self['list'].instance.moveSelectionTo(0)
            if self.sel.endswith('.zip'):
                remove(self.BackupDirectory + self.sel)
            else:
                rmtree(self.BackupDirectory + self.sel)
        self.populate_List()

    def GreenPressed(self):
        backup = None
        self.BackupRunning = False
        for job in Components.Task.job_manager.getPendingJobs():
            if job.name.startswith(_('Image Manager')):
                backup = job
                self.BackupRunning = True

        if self.BackupRunning and backup:
            self.showJobView(backup)
        else:
            self.keyBackup()
        return

    def keyBackup(self):
        message = _('Are you ready to create a backup image ?')
        ybox = self.session.openWithCallback(self.doBackup, MessageBox, message, MessageBox.TYPE_YESNO)
        ybox.setTitle(_('Backup Confirmation'))

    def doBackup(self, answer):
        backup = None
        if answer is True:
            self.ImageBackup = ImageBackup(self.session)
            Components.Task.job_manager.AddJob(self.ImageBackup.createBackupJob())
            self.BackupRunning = True
            self['key_green'].setText(_('View Progress'))
            self['key_green'].show()
            for job in Components.Task.job_manager.getPendingJobs():
                if job.name.startswith(_('Image Manager')):
                    backup = job

            if backup:
                self.showJobView(backup)
        return

    def keyResstore(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            if getBrandOEM() == 'dreambox':
                self.session.open(MessageBox, _('Dreambox not support restore via USB, please use Web restore'), MessageBox.TYPE_INFO, timeout=10)
            else:
                message = _('Are you sure you want to restore this image:\n ') + self.sel
                ybox = self.session.openWithCallback(self.keyResstore2, MessageBox, message, MessageBox.TYPE_YESNO)
                ybox.setTitle(_('Restore Confirmation'))
        else:
            self.session.open(MessageBox, _('You have no image to restore.'), MessageBox.TYPE_INFO, timeout=10)

    def keyResstore2(self, answer):
        if path.islink('/tmp/imagerestore'):
            unlink('/tmp/imagerestore')
        if answer:
            self.session.open(MessageBox, _('Please wait while the restore prepares'), MessageBox.TYPE_INFO, timeout=60, enable_input=False)
            TEMPDESTROOT = self.BackupDirectory + 'imagerestore'
            if self.sel.endswith('.zip'):
                if not path.exists(TEMPDESTROOT):
                    mkdir(TEMPDESTROOT, 493)
                self.Console.ePopen('unzip -o ' + self.BackupDirectory + self.sel + ' -d ' + TEMPDESTROOT, self.keyResstore3)
                symlink(TEMPDESTROOT, '/tmp/imagerestore')
            else:
                symlink(self.BackupDirectory + self.sel, '/tmp/imagerestore')
                self.keyResstore3(0, 0)

    def keyResstore3(self, result, retval, extra_args = None):
        if retval == 0:
            kernelMTD = getMachineMtdKernel()
            kernelFILE = getMachineKernelFile()
            rootMTD = getMachineMtdRoot()
            rootFILE = getMachineRootFile()
            MAINDEST = '/tmp/imagerestore/' + getImageFolder() + '/'
            config.imagemanager.restoreimage.setValue(self.sel)
            self.Console.ePopen('ofgwrite -r -k -r' + rootMTD + ' -k' + kernelMTD + ' ' + MAINDEST)


class AutoImageManagerTimer():

    def __init__(self, session):
        global BackupTime
        self.session = session
        self.backuptimer = eTimer()
        self.backuptimer.callback.append(self.BackuponTimer)
        self.backupactivityTimer = eTimer()
        self.backupactivityTimer.timeout.get().append(self.backupupdatedelay)
        now = int(time())
        if config.imagemanager.schedule.value:
            print '[ImageManager] Backup Schedule Enabled at ', strftime('%c', localtime(now))
            if now > 1262304000:
                self.backupupdate()
            else:
                print '[ImageManager] Backup Time not yet set.'
                BackupTime = 0
                self.backupactivityTimer.start(36000)
        else:
            BackupTime = 0
            print '[ImageManager] Backup Schedule Disabled at', strftime('(now=%c)', localtime(now))
            self.backupactivityTimer.stop()

    def backupupdatedelay(self):
        self.backupactivityTimer.stop()
        self.backupupdate()

    def getBackupTime(self):
        backupclock = config.imagemanager.scheduletime.value
        nowt = time()
        now = localtime(nowt)
        return int(mktime((now.tm_year,
         now.tm_mon,
         now.tm_mday,
         backupclock[0],
         backupclock[1],
         0,
         now.tm_wday,
         now.tm_yday,
         now.tm_isdst)))

    def backupupdate(self, atLeast = 0):
        global BackupTime
        self.backuptimer.stop()
        BackupTime = self.getBackupTime()
        now = int(time())
        if BackupTime > 0:
            if BackupTime < now + atLeast:
                if config.imagemanager.repeattype.value == 'daily':
                    BackupTime += 86400
                    while int(BackupTime) - 30 < now:
                        BackupTime += 86400

                elif config.imagemanager.repeattype.value == 'weekly':
                    BackupTime += 604800
                    while int(BackupTime) - 30 < now:
                        BackupTime += 604800

                elif config.imagemanager.repeattype.value == 'monthly':
                    BackupTime += 2592000
                    while int(BackupTime) - 30 < now:
                        BackupTime += 2592000

            next = BackupTime - now
            self.backuptimer.startLongTimer(next)
        else:
            BackupTime = -1
        print '[ImageManager] Backup Time set to', strftime('%c', localtime(BackupTime)), strftime('(now=%c)', localtime(now))
        return BackupTime

    def backupstop(self):
        self.backuptimer.stop()

    def BackuponTimer(self):
        self.backuptimer.stop()
        now = int(time())
        wake = self.getBackupTime()
        atLeast = 0
        if wake - now < 60:
            print '[ImageManager] Backup onTimer occured at', strftime('%c', localtime(now))
            from Screens.Standby import inStandby
            if not inStandby:
                message = _('Your %s %s is about to run a full image backup, this can take about 6 minutes to complete,\ndo you want to allow this?') % (getMachineBrand(), getMachineName())
                ybox = self.session.openWithCallback(self.doBackup, MessageBox, message, MessageBox.TYPE_YESNO, timeout=30)
                ybox.setTitle('Scheduled Backup.')
            else:
                print '[ImageManager] in Standby, so just running backup', strftime('%c', localtime(now))
                self.doBackup(True)
        else:
            print '[ImageManager] Where are not close enough', strftime('%c', localtime(now))
            self.backupupdate(60)

    def doBackup(self, answer):
        now = int(time())
        if answer is False:
            if config.imagemanager.backupretrycount.value < 2:
                print '[ImageManager] Number of retries', config.imagemanager.backupretrycount.value
                print '[ImageManager] Backup delayed.'
                repeat = config.imagemanager.backupretrycount.value
                repeat += 1
                config.imagemanager.backupretrycount.setValue(repeat)
                BackupTime = now + int(config.imagemanager.backupretry.value) * 60
                print '[ImageManager] Backup Time now set to', strftime('%c', localtime(BackupTime)), strftime('(now=%c)', localtime(now))
                self.backuptimer.startLongTimer(int(config.imagemanager.backupretry.value) * 60)
            else:
                atLeast = 60
                print '[ImageManager] Enough Retries, delaying till next schedule.', strftime('%c', localtime(now))
                self.session.open(MessageBox, _('Enough Retries, delaying till next schedule.'), MessageBox.TYPE_INFO, timeout=10)
                config.imagemanager.backupretrycount.setValue(0)
                self.backupupdate(atLeast)
        else:
            print '[ImageManager] Running Backup', strftime('%c', localtime(now))
            self.ImageBackup = ImageBackup(self.session)
            Components.Task.job_manager.AddJob(self.ImageBackup.createBackupJob())


class ImageBackup(Screen):

    def __init__(self, session, updatebackup = False):
        Screen.__init__(self, session)
        self.Console = Console()
        self.BackupDevice = config.imagemanager.backuplocation.value
        print '[ImageManager] Device: ' + self.BackupDevice
        self.BackupDirectory = config.imagemanager.backuplocation.value + 'imagebackups/'
        print '[ImageManager] Directory: ' + self.BackupDirectory
        self.BackupDate = getImageVersion() + '.' + getImageBuild() + '-' + strftime('%Y%m%d_%H%M%S', localtime())
        self.WORKDIR = self.BackupDirectory + config.imagemanager.folderprefix.value + '-temp'
        self.TMPDIR = self.BackupDirectory + config.imagemanager.folderprefix.value + '-mount'
        if updatebackup:
            self.MAINDESTROOT = self.BackupDirectory + config.imagemanager.folderprefix.value + '-SoftwareUpdate-' + self.BackupDate
        else:
            self.MAINDESTROOT = self.BackupDirectory + config.imagemanager.folderprefix.value + '-' + self.BackupDate
        self.kernelMTD = getMachineMtdKernel()
        self.kernelFILE = getMachineKernelFile()
        self.rootMTD = getMachineMtdRoot()
        self.rootFILE = getMachineRootFile()
        self.MAINDEST = self.MAINDESTROOT + '/' + getImageFolder() + '/'
        print 'MTD: Kernel:', self.kernelMTD
        print 'MTD: Root:', self.rootMTD
        if getImageFileSystem() == 'ubi' or getImageFileSystem() == 'ubi.nfi':
            self.ROOTFSTYPE = 'ubifs'
        else:
            self.ROOTFSTYPE = 'jffs2'
        self.swapdevice = ''
        self.RamChecked = False
        self.SwapCreated = False
        self.Stage1Completed = False
        self.Stage2Completed = False
        self.Stage3Completed = False
        self.Stage4Completed = False
        self.Stage5Completed = False

    def createBackupJob(self):
        job = Components.Task.Job(_('Image Manager'))
        task = Components.Task.PythonTask(job, _('Setting Up...'))
        task.work = self.JobStart
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Checking Free RAM..'), timeoutCount=10)
        task.check = lambda : self.RamChecked
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Creating Swap..'), timeoutCount=120)
        task.check = lambda : self.SwapCreated
        task.weighting = 5
        task = Components.Task.PythonTask(job, _('Backing up Root file system...'))
        task.work = self.doBackup1
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Backing up Root file system...'), timeoutCount=900)
        task.check = lambda : self.Stage1Completed
        task.weighting = 35
        task = Components.Task.PythonTask(job, _('Backing up Kernel...'))
        task.work = self.doBackup2
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Backing up Kernel...'), timeoutCount=900)
        task.check = lambda : self.Stage2Completed
        task.weighting = 15
        task = Components.Task.PythonTask(job, _('Removing temp mounts...'))
        task.work = self.doBackup3
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Removing temp mounts...'), timeoutCount=900)
        task.check = lambda : self.Stage3Completed
        task.weighting = 5
        task = Components.Task.PythonTask(job, _('Moving to Backup Location...'))
        task.work = self.doBackup4
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Moving to Backup Location...'), timeoutCount=900)
        task.check = lambda : self.Stage4Completed
        task.weighting = 5
        task = Components.Task.PythonTask(job, _('Creating zip...'))
        task.work = self.doBackup5
        task.weighting = 5
        task = Components.Task.ConditionTask(job, _('Creating zip...'), timeoutCount=900)
        task.check = lambda : self.Stage5Completed
        task.weighting = 5
        task = Components.Task.PythonTask(job, _('Backup Complete...'))
        task.work = self.BackupComplete
        task.weighting = 5
        return job

    def JobStart(self):
        try:
            if not path.exists(self.BackupDirectory):
                mkdir(self.BackupDirectory, 493)
            if path.exists(self.BackupDirectory + config.imagemanager.folderprefix.value + '-swapfile_backup'):
                system('swapoff ' + self.BackupDirectory + config.imagemanager.folderprefix.value + '-swapfile_backup')
                remove(self.BackupDirectory + config.imagemanager.folderprefix.value + '-swapfile_backup')
        except Exception as e:
            print str(e)
            print 'Device: ' + config.imagemanager.backuplocation.value + ", i don't seem to have write access to this device."

        s = statvfs(self.BackupDevice)
        free = s.f_bsize * s.f_bavail / 1048576
        if int(free) < 200:
            AddPopupWithCallback(self.BackupComplete, _('The backup location does not have enough free space.' + '\n' + self.BackupDevice + 'only has ' + str(free) + 'MB free.'), MessageBox.TYPE_INFO, 10, 'RamCheckFailedNotification')
        else:
            self.MemCheck()

    def MemCheck(self):
        memfree = 0
        swapfree = 0
        f = open('/proc/meminfo', 'r')
        for line in f.readlines():
            if line.find('MemFree') != -1:
                parts = line.strip().split()
                memfree = int(parts[1])
            elif line.find('SwapFree') != -1:
                parts = line.strip().split()
                swapfree = int(parts[1])

        f.close()
        TotalFree = memfree + swapfree
        print '[ImageManager] Stage1: Free Mem', TotalFree
        if int(TotalFree) < 3000:
            supported_filesystems = frozenset(('ext4', 'ext3', 'ext2'))
            candidates = []
            mounts = getProcMounts()
            for partition in harddiskmanager.getMountedPartitions(False, mounts):
                if partition.filesystem(mounts) in supported_filesystems:
                    candidates.append((partition.description, partition.mountpoint))

            for swapdevice in candidates:
                self.swapdevice = swapdevice[1]

            if self.swapdevice:
                print '[ImageManager] Stage1: Creating Swapfile.'
                self.RamChecked = True
                self.MemCheck2()
            else:
                print '[ImageManager] Sorry, not enough free ram found, and no physical devices that supports SWAP attached'
                AddPopupWithCallback(self.BackupComplete, _("Sorry, not enough free ram found, and no physical devices that supports SWAP attached. Can't create Swapfile on network or fat32 filesystems, unable to make backup"), MessageBox.TYPE_INFO, 10, 'RamCheckFailedNotification')
        else:
            print '[ImageManager] Stage1: Found Enough Ram'
            self.RamChecked = True
            self.SwapCreated = True

    def MemCheck2(self):
        self.Console.ePopen('dd if=/dev/zero of=' + self.swapdevice + config.imagemanager.folderprefix.value + '-swapfile_backup bs=1024 count=61440', self.MemCheck3)

    def MemCheck3(self, result, retval, extra_args = None):
        if retval == 0:
            self.Console.ePopen('mkswap ' + self.swapdevice + config.imagemanager.folderprefix.value + '-swapfile_backup', self.MemCheck4)

    def MemCheck4(self, result, retval, extra_args = None):
        if retval == 0:
            self.Console.ePopen('swapon ' + self.swapdevice + config.imagemanager.folderprefix.value + '-swapfile_backup', self.MemCheck5)

    def MemCheck5(self, result, retval, extra_args = None):
        self.SwapCreated = True

    def doBackup1(self):
        print '[ImageManager] Stage1: Creating tmp folders.', self.BackupDirectory
        print '[ImageManager] Stage1: Creating backup Folders.'
        if path.exists(self.WORKDIR):
            rmtree(self.WORKDIR)
        mkdir(self.WORKDIR, 420)
        print '[ImageManager] Stage1: Create root folder.'
        if path.exists(self.TMPDIR + '/root') and path.ismount(self.TMPDIR + '/root'):
            system('umount ' + self.TMPDIR + '/root')
        elif path.exists(self.TMPDIR + '/root'):
            rmtree(self.TMPDIR + '/root')
        if getMachineBuild() in ('dm800', 'dm800se', 'dm500hd'):
            print '[ImageManager] Stage1: Create boot folder.'
            if path.exists(self.TMPDIR + '/boot') and path.ismount(self.TMPDIR + '/boot'):
                system('umount ' + self.TMPDIR + '/boot')
            elif path.exists(self.TMPDIR + '/boot'):
                rmtree(self.TMPDIR + '/boot')
        if path.exists(self.TMPDIR):
            rmtree(self.TMPDIR)
        makedirs(self.TMPDIR + '/root', 420)
        if getMachineBuild() in ('dm800', 'dm800se', 'dm500hd'):
            print '[ImageManager] Stage1: Create boot folder only dm800 dm800se dm500hd'
            makedirs(self.TMPDIR + '/boot', 420)
        makedirs(self.MAINDESTROOT, 420)
        self.commands = []
        print '[ImageManager] Stage1: Making Root Image.'
        if not getBrandOEM() == 'dreambox':
            makedirs(self.MAINDEST, 420)
        if getBrandOEM() == 'dreambox':
            print '[ImageManager] Stage1: Dreambox Detected.'
            if path.exists('/dev/mtd/1'):
                MTDDEV = '/dev/mtd/1'
            else:
                MTDDEV = '/dev/mtd1'
            if path.exists('/tmp/secondstage.bin'):
                print '[ImageManager] Stage1: SecondStage Detected.'
                move('/tmp/secondstage.bin ', self.WORKDIR + '/secondstage.bin')
            else:
                print '[ImageManager] Stage1: SecondStage Not Detected. Dumping...'
                self.commands.append('nanddumpdm --noecc --omitoob --bb=skipbad --truncate --file ' + self.WORKDIR + '/secondstage.bin ' + MTDDEV)
        if self.ROOTFSTYPE == 'jffs2':
            print '[ImageManager] Stage1: JFFS2 Detected.'
            if getMachineBuild() == 'gb800solo':
                JFFS2OPTIONS = ' --disable-compressor=lzo -e131072 -l -p125829120'
            elif getBoxType() == 'dm800' or getBoxType() == 'dm800se' or getBoxType() == 'dm500hd':
                JFFS2OPTIONS = ' --eraseblock=0x4000 -n -l'
            else:
                print '[ImageManager] Stage1: Else OK'
                JFFS2OPTIONS = ' --disable-compressor=lzo --eraseblock=0x20000 -n -l'
            print '[ImageManager] Stage1: Mount prima OK'
            self.commands.append('mount --bind / ' + self.TMPDIR + '/root')
            self.commands.append('mkfs.jffs2 --root=' + self.TMPDIR + '/root --faketime --output=' + self.WORKDIR + '/root.jffs2' + JFFS2OPTIONS)
            print '[ImageManager] Stage1: Mount dopo OK'
            if getMachineBuild() in ('dm800', 'dm800se', 'dm500hd'):
                self.commands.append('mount -t jffs2 /dev/mtdblock/2 ' + self.TMPDIR + '/boot')
                self.commands.append('mkfs.jffs2 --root=' + self.TMPDIR + '/boot --faketime --output=' + self.WORKDIR + '/boot.jffs2' + JFFS2OPTIONS)
        else:
            print '[ImageManager] Stage1: UBIFS Detected.'
            UBINIZE = 'ubinize'
            UBINIZE_ARGS = getMachineUBINIZE()
            MKUBIFS_ARGS = getMachineMKUBIFS()
            output = open(self.WORKDIR + '/ubinize.cfg', 'w')
            output.write('[ubifs]\n')
            output.write('mode=ubi\n')
            output.write('image=' + self.WORKDIR + '/root.ubi\n')
            output.write('vol_id=0\n')
            output.write('vol_type=dynamic\n')
            output.write('vol_name=rootfs\n')
            output.write('vol_flags=autoresize\n')
            output.close()
            self.commands.append('mount --bind / ' + self.TMPDIR + '/root')
            self.commands.append('touch ' + self.WORKDIR + '/root.ubi')
            self.commands.append('mkfs.ubifs -r ' + self.TMPDIR + '/root -o ' + self.WORKDIR + '/root.ubi ' + MKUBIFS_ARGS)
            self.commands.append('ubinize -o ' + self.WORKDIR + '/root.ubifs ' + UBINIZE_ARGS + ' ' + self.WORKDIR + '/ubinize.cfg')
        self.Console.eBatch(self.commands, self.Stage1Complete, debug=False)

    def Stage1Complete(self, extra_args = None):
        if len(self.Console.appContainers) == 0:
            self.Stage1Completed = True
            print '[ImageManager] Stage1: Complete.'

    def doBackup2(self):
        print '[ImageManager] Stage2: Making Kernel Image.'
        if getBrandOEM() in 'dreambox':
            if getMachineBuild() in ('dm800', 'dm800se', 'dm500hd'):
                NFIDUMP = 'buildimage --arch ' + getMachineBuild() + ' --brcmnand --erase-block-size 0x4000 --flash-size 0x4000000 --sector-size 512 --boot-partition 0x40000:' + self.WORKDIR + '/secondstage.bin --data-partition 0x3C0000:' + self.WORKDIR + '/boot.jffs2 --data-partition 0x3C00000:' + self.WORKDIR + '/root.jffs2 > ' + self.MAINDEST + '/' + config.imagemanager.folderprefix.value + '-' + self.BackupDate + '.nfi'
                self.command = NFIDUMP
            elif getMachineBuild() == 'dm8000':
                NFIDUMP = 'buildimage --arch ' + getMachineBuild() + ' --erase-block-size 0x20000 --flash-size 0x10000000 --sector-size 2048 --boot-partition 0x100000:' + self.WORKDIR + '/secondstage.bin --data-partition 0x700000:' + self.WORKDIR + '/boot.ubifs --data-partition 0xF800000:' + self.WORKDIR + '/root.ubifs > ' + self.MAINDEST + '/' + config.imagemanager.folderprefix.value + '-' + self.BackupDate + '.nfi'
                self.command = 'nanddumpdm --noecc --omitoob --bb=skipbad --quiet --file ' + self.WORKDIR + '/boot.ubifs ' + '/dev/mtd2' + ' && ' + NFIDUMP
            elif getMachineBuild() in ('dm7020hd', 'dm7020hdv2'):
                NFIDUMP = 'buildimage --arch ' + getMachineBuild() + ' --hw-ecc --brcmnand --erase-block-size 0x40000 --flash-size 0x40000000 --sector-size 4096 --boot-partition 0x100000:' + self.WORKDIR + '/secondstage.bin --data-partition 0x700000:' + self.WORKDIR + '/boot.ubifs --data-partition 0x3F800000:' + self.WORKDIR + '/root.ubifs > ' + self.MAINDEST + '/' + config.imagemanager.folderprefix.value + '-' + self.BackupDate + '.nfi'
                self.command = 'nanddumpdm --noecc --omitoob --bb=skipbad --quiet --file ' + self.WORKDIR + '/boot.ubifs ' + '/dev/mtd2' + ' && ' + NFIDUMP
            elif getMachineBuild() in ('dm800sev2', 'dm500hdv2'):
                NFIDUMP = 'buildimage --arch ' + getMachineBuild() + ' --hw-ecc --brcmnand --erase-block-size 0x20000 --flash-size 0x40000000 --sector-size 2048 --boot-partition 0x100000:' + self.WORKDIR + '/secondstage.bin --data-partition 0x700000:' + self.WORKDIR + '/boot.ubifs --data-partition 0x3F800000:' + self.WORKDIR + '/root.ubifs > ' + self.MAINDEST + '/' + config.imagemanager.folderprefix.value + '-' + self.BackupDate + '.nfi'
                self.command = 'nanddumpdm --noecc --omitoob --bb=skipbad --quiet --file ' + self.WORKDIR + '/boot.ubifs ' + '/dev/mtd2' + ' && ' + NFIDUMP
                print self.command
        else:
            self.command = 'nanddump /dev/' + self.kernelMTD + ' -f ' + self.WORKDIR + '/vmlinux.gz'
        self.Console.ePopen(self.command, self.Stage2Complete)

    def Stage2Complete(self, result, retval, extra_args = None):
        if retval == 0:
            self.Stage2Completed = True
            print '[ImageManager] Stage2: Complete.'

    def doBackup3(self):
        print '[ImageManager] Stage3: Unmounting and removing tmp system'
        if path.exists(self.TMPDIR + '/root') and path.exists(self.TMPDIR + '/boot'):
            self.command = 'umount ' + self.TMPDIR + '/root && umount ' + self.TMPDIR + '/boot && rm -rf ' + self.TMPDIR
            self.Console.ePopen(self.command, self.Stage3Complete)
        elif path.exists(self.TMPDIR + '/root'):
            self.command = 'umount ' + self.TMPDIR + '/root && rm -rf ' + self.TMPDIR
            self.Console.ePopen(self.command, self.Stage3Complete)

    def Stage3Complete(self, result, retval, extra_args = None):
        if retval == 0:
            self.Stage3Completed = True
            print '[ImageManager] Stage3: Complete.'

    def doBackup4(self):
        print '[ImageManager] Stage4: Moving from work to backup folders'
        if not getBrandOEM() == 'dreambox':
            move(self.WORKDIR + '/root.' + self.ROOTFSTYPE, self.MAINDEST + '/' + self.rootFILE)
            move(self.WORKDIR + '/vmlinux.gz', self.MAINDEST + '/' + self.kernelFILE)
        if getBrandOEM() in ('vuplus', 'sunray'):
            fileout = open(self.MAINDEST + '/reboot.update', 'w')
            line = 'This file forces a reboot after the update.'
            fileout.write(line)
            fileout.close()
            fileout = open(self.MAINDEST + '/imageversion', 'w')
            line = 'Italysat-' + self.BackupDate
            fileout.write(line)
            fileout.close()
            imagecreated = True
        elif getBrandOEM() == 'dreambox':
            fileout = open(self.MAINDEST + '/imageversion', 'w')
            line = 'Italysat-' + self.BackupDate
            fileout.write(line)
            fileout.close()
            imagecreated = True
        elif getMachineBuild() in ('cloudibox2plus', 'cloudibox3', 'cloudibox3se'):
            fileout = open(self.MAINDEST + '/force', 'w')
            line = "rename this file to 'force' to force an update without confirmation"
            fileout.write(line)
            fileout.close()
            fileout = open(self.MAINDEST + '/imageversion', 'w')
            line = 'Italysat-' + self.BackupDate
            fileout.write(line)
            fileout.close()
        elif getMachineBuild() in ('gb800solo', 'gb800se'):
            fileout = open(self.MAINDEST + '/noforce', 'w')
            line = "rename this file to 'force' to force an update without confirmation"
            fileout.write(line)
            fileout.close()
            fileout = open(self.MAINDEST + '/imageversion', 'w')
            line = 'Italysat-' + self.BackupDate
            fileout.write(line)
            fileout.close()
            copy('/usr/lib/enigma2/python/Plugins/SystemPlugins/ItalyCore/burn-solo.bat', self.MAINDESTROOT + '/burn.bat')
        else:
            fileout = open(self.MAINDEST + '/noforce', 'w')
            line = "rename this file to 'force' to force an update without confirmation"
            fileout.write(line)
            fileout.close()
            fileout = open(self.MAINDEST + '/imageversion', 'w')
            line = 'Italysat-' + self.BackupDate
            fileout.write(line)
            fileout.close()
        imagecreated = True
        print '[ImageManager] Stage4: Removing Swap.'
        if path.exists(self.swapdevice + config.imagemanager.folderprefix.value + '-swapfile_backup'):
            system('swapoff ' + self.swapdevice + config.imagemanager.folderprefix.value + '-swapfile_backup')
            remove(self.swapdevice + config.imagemanager.folderprefix.value + '-swapfile_backup')
        if path.exists(self.WORKDIR):
            rmtree(self.WORKDIR)
        if path.exists(self.MAINDEST + '/' + self.rootFILE) and path.exists(self.MAINDEST + '/' + self.kernelFILE):
            for root, dirs, files in walk(self.MAINDEST):
                for momo in dirs:
                    chmod(path.join(root, momo), 420)

                for momo in files:
                    chmod(path.join(root, momo), 420)

            print '[ImageManager] Stage4: Image created in ' + self.MAINDESTROOT
            self.Stage4Complete()
        elif path.exists(self.MAINDEST + '/' + config.imagemanager.folderprefix.value + '-' + self.BackupDate + '.nfi'):
            print '[ImageManager] Stage4: Image created in ' + self.MAINDESTROOT
            self.Stage4Complete()
        else:
            print '[ImageManager] Stage4: Image creation failed - e. g. wrong backup destination or no space left on backup device'
            self.BackupComplete()

    def Stage4Complete(self):
        self.Stage4Completed = True
        print '[ImageManager] Stage4: Complete.'

    def doBackup5(self):
        print '[ImageManager] Stage5: Create zip.'
        zipfolder = path.split(self.MAINDESTROOT)
        self.commands = []
        self.commands.append('cd ' + self.MAINDESTROOT + ' && zip -r ' + self.MAINDESTROOT + '.zip *')
        self.commands.append('rm -rf ' + self.MAINDESTROOT)
        self.Console.eBatch(self.commands, self.Stage5Complete, debug=False)

    def Stage5Complete(self, anwser = None):
        self.Stage5Completed = True
        print '[ImageManager] Stage5: Complete.'

    def BackupComplete(self, anwser = None):
        if config.imagemanager.schedule.value:
            atLeast = 60
            autoImageManagerTimer.backupupdate(atLeast)
        else:
            autoImageManagerTimer.backupstop()


class ImageManagerDownload(Screen):

    def __init__(self, session, BackupDirectory):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Image Manager'))
        self.BackupDirectory = BackupDirectory
        self['lab1'] = Label(_('Select an image to Download:'))
        self['key_red'] = Button(_('Close'))
        self['key_green'] = Button(_('Download'))
        self.onChangedEntry = []
        self.emlist = []
        self['list'] = MenuList(self.emlist)
        self.populate_List()
        if self.selectionChanged not in self['list'].onSelectionChanged:
            self['list'].onSelectionChanged.append(self.selectionChanged)

    def selectionChanged(self):
        for x in self.onChangedEntry:
            x()

    def populate_List(self):
        try:
            self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'], {'cancel': self.close,
             'red': self.close,
             'green': self.keyDownload,
             'ok': self.keyDownload}, -1)
            if not path.exists(self.BackupDirectory):
                mkdir(self.BackupDirectory, 493)
            import urllib2
            from bs4 import BeautifulSoup
            if getMachineMake() == 'vuuno':
                self.boxtype = 'Vu+Uno'
            elif getMachineMake() == 'vuultimo':
                self.boxtype = 'Vu+Ultimo'
            elif getMachineMake() == 'vusolo':
                self.boxtype = 'Vu+Solo'
            elif getMachineMake() == 'vusolose':
                self.boxtype = 'Vu+Solo-SE'
            elif getMachineMake() == 'vusolo2':
                self.boxtype = 'Vu+Solo2'
            elif getMachineMake() == 'vuduo':
                self.boxtype = 'Vu+Duo'
            elif getMachineMake() == 'vuduo2':
                self.boxtype = 'Vu+Duo2'
            elif getMachineMake() == 'vuzero':
                self.boxtype = 'Vu+Zero'
            elif getMachineMake() == 'et4x00':
                self.boxtype = 'ET-4x00'
            elif getMachineMake() == 'et5x00':
                self.boxtype = 'ET-5x00'
            elif getMachineMake() == 'et6x00':
                self.boxtype = 'ET-6x00'
            elif getMachineMake() == 'et8000':
                self.boxtype = 'ET-8x00'
            elif getMachineMake() == 'et9x00':
                self.boxtype = 'ET-9x00'
            elif getMachineMake() == 'et10000':
                self.boxtype = 'ET-10x00'
            elif getMachineMake() == 'tmtwin':
                self.boxtype = 'TM-Twin-OE'
            elif getMachineMake() == 'tm2t':
                self.boxtype = 'TM-2T'
            elif getMachineMake() == 'tmsingle':
                self.boxtype = 'TM-Single'
            elif getMachineMake() == 'tmnano':
                self.boxtype = 'TM-Nano-OE'
            elif getMachineMake() == 'tmnanose':
                self.boxtype = 'TM-Nano-SE'
            elif getMachineMake() == 'tmnano2t':
                self.boxtype = 'TM-Nano-2T'
            elif getMachineMake() == 'tmnano3t':
                self.boxtype = 'TM-Nano-3T'
            elif getMachineMake() == 'tmnano2super':
                self.boxtype = 'TM-Nano2-Super'
            elif getMachineMake() == 'iqonios100hd':
                self.boxtype = 'iqon-IOS-100HD'
            elif getMachineMake() == 'iqonios200hd':
                self.boxtype = 'iqon-IOS-200HD'
            elif getMachineMake() == 'iqonios300hd':
                self.boxtype = 'iqon-IOS-300HD'
            elif getMachineMake() == 'maram9':
                self.boxtype = 'Mara-M9'
            elif getMachineMake() == 'mutant2400':
                self.boxtype = 'Mutant-HD2400'
            elif getMachineMake() == 'xp1000max':
                self.boxtype = 'MaxDigital-XP1000'
            elif getMachineMake() == 'xp1000plus':
                self.boxtype = 'OCTAGON-XP1000PLUS'
            elif getMachineMake() == 'sf8':
                self.boxtype = 'OCTAGON-SF8-HD'
            elif getMachineMake() == 'qb800solo':
                self.boxtype = 'GiGaBlue-HD800Solo'
            elif getMachineMake() == 'gb800se':
                self.boxtype = 'GiGaBlue-HD800SE'
            elif getMachineMake() == 'gb800ue':
                self.boxtype = 'GiGaBlue-HD800UE'
            elif getMachineMake() == 'gb800seplus':
                self.boxtype = 'GiGaBlue-HD800SE-PLUS'
            elif getMachineMake() == 'gb800ueplus':
                self.boxtype = 'GiGaBlue-HD800UE-PLUS'
            elif getMachineMake() == 'gbquad':
                self.boxtype = 'GiGaBlue-HD-QUAD'
            elif getMachineMake() == 'gbquadplus':
                self.boxtype = 'GiGaBlue-HD-QUAD-PLUS'
            elif getMachineMake() == 'ventonhdx':
                self.boxtype = 'Venton-Unibox-HDx'
            elif getMachineMake() == 'uniboxhde':
                self.boxtype = 'Venton-Unibox-HDeco-PLUS'
            elif getMachineMake() == 'mbtwin':
                self.boxtype = 'Miraclebox-Twin'
            elif getMachineMake() == 'mbmini':
                self.boxtype = 'Miraclebox-Mini'
            elif getMachineMake() == 'mbultra':
                self.boxtype = 'Miraclebox-Ultra'
            elif getMachineMake() == 'xpeedlx':
                self.boxtype = 'GI-Xpeed-LX'
            elif getMachineMake() == 'xpeedlx3':
                self.boxtype = 'GI-Xpeed-LX3'
            elif getMachineMake() == 'axodinc':
                self.boxtype = 'Opticum-AX-ODIN-DVBC-1'
            elif getMachineMake() == 'ixusszero':
                self.boxtype = 'Medialink-IXUSS-ZERO'
            elif getMachineMake() == 'dm500hd':
                self.boxtype = 'Dreambox-500hd'
            elif getMachineMake() == 'dm500hdv2':
                self.boxtype = 'Dreambox-500hdv2'
            elif getMachineMake() == 'dm800':
                self.boxtype = 'Dreambox-800'
            elif getMachineMake() == 'dm8000':
                self.boxtype = 'Dreambox-8000'
            elif getMachineMake() == 'dm800se':
                self.boxtype = 'Dreambox-800se'
            elif getMachineMake() == 'dm800sev2':
                self.boxtype = 'Dreambox-800sev2'
            elif getMachineMake() == 'dm7020hd':
                self.boxtype = 'Dreambox-7020hd'
            elif getMachineMake() == 'dm7020hd':
                self.boxtype = 'Dreambox-7020hd'
            elif getMachineMake() == 'dm7020hdv2':
                self.boxtype = 'Dreambox-7020hdv2'
            elif getMachineMake() == 'dm800sev2':
                self.boxtype = 'Dreambox-800sev2'
            elif getMachineMake() == 'dm500hdv2':
                self.boxtype = 'Dreambox-500hdv2'
            elif getMachineMake() == 'e3hd':
                self.boxtype = 'E3HD'
            elif getMachineMake() == 'mediabox':
                self.boxtype = 'Mediabox-LX1'
            elif getMachineMake() == 'atemio5x00':
                self.boxtype = 'Atemio-5200HD'
            elif getMachineMake() == 'atemio8x00':
                self.boxtype = 'Atemio-Nemesis'
            elif getMachineMake() == 'icloudbox2plus':
                self.boxtype = 'Cloud-Ibox-2Plus'
            elif getMachineMake() == 'icloudbox3':
                self.boxtype = 'Cloud-Ibox-3'
            elif getMachineMake() == 'zgemmash1':
                self.boxtype = 'Zgemma-Sh1'
            elif getMachineMake() == 'zgemmash2':
                self.boxtype = 'Zgemma-Sh2'
            elif getMachineMake() == 'zgemmas2s':
                self.boxtype = 'Zgemma-S2s'
            url = 'http://www.openvix.co.uk/openvix-builds/' + self.boxtype + '/'
            conn = urllib2.urlopen(url)
            html = conn.read()
            soup = BeautifulSoup(html)
            links = soup.find_all('a')
            del self.emlist[:]
            for tag in links:
                link = tag.get('href', None)
                if link != None and link.endswith('zip') and link.find(getMachineMake()) != -1:
                    self.emlist.append(str(link))

            self.emlist.sort()
            self.emlist.reverse()
        except:
            self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'], {'cancel': self.close,
             'red': self.close}, -1)
            self.emlist.append(' ')
            self['list'].setList(self.emlist)
            self['list'].show()

        return

    def keyDownload(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            message = _('Are you sure you want to download this image:\n ') + self.sel
            ybox = self.session.openWithCallback(self.doDownload, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Download Confirmation'))
        else:
            self.session.open(MessageBox, _('You have no image to download.'), MessageBox.TYPE_INFO, timeout=10)

    def doDownload(self, answer):
        if answer is True:
            self.selectedimage = self['list'].getCurrent()
            file = self.BackupDirectory + self.selectedimage
            mycmd1 = _("echo 'Downloading Image.'")
            mycmd2 = 'wget -q http://download.italysat.eu/italysat/' + self.boxtype + '/' + self.selectedimage + ' -O ' + self.BackupDirectory + 'image.zip'
            mycmd3 = 'mv ' + self.BackupDirectory + 'image.zip ' + file
            self.session.open(ScreenConsole, title=_('Downloading Image...'), cmdlist=[mycmd1, mycmd2, mycmd3], closeOnSuccess=True)

    def myclose(self, result, retval, extra_args):
        remove(self.BackupDirectory + self.selectedimage)
        self.close()