# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatDownloader.py
from enigma import eTimer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists
from os import remove

class ItalyDownloader(Screen):
    EVENT_DONE = 10
    EVENT_KILLED = 5
    EVENT_CURR = 0

    def __init__(self, session, url, folder, filename):
        Screen.__init__(self, session)
        self.url = url
        self.filename = filename
        self.dstfilename = folder + filename
        self['oktext'] = Label(_('OK'))
        self['canceltext'] = Label(_('Cancel'))
        self['fname'] = StaticText('')
        self['status'] = StaticText('')
        self['progressbar'] = Progress()
        self['progressbar'].range = 1000
        self['progressbar'].value = 0
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.cancel,
         'back': self.cancel,
         'red': self.stop,
         'green': self.cancel}, -1)
        self.autoCloseTimer = eTimer()
        self.autoCloseTimer.timeout.get().append(self.cancel)
        self.startDownloadTimer = eTimer()
        self.startDownloadTimer.timeout.get().append(self.fileDownload)
        self.download = None
        self.downloading(False)
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.startDownload)
        return

    def setWindowTitle(self):
        self.setTitle(_('Downloading...'))

    def startDownload(self):
        self['progressbar'].value = 0
        self.startDownloadTimer.start(250, True)

    def downloading(self, state = True):
        if state:
            self['canceltext'].show()
            self['oktext'].hide()
        else:
            self.download = None
            self['canceltext'].hide()
            self['oktext'].show()
        return

    def fileDownload(self):
        from Tools.Downloader import downloadWithProgress
        self.download = downloadWithProgress(self.url, self.dstfilename)
        self.download.addProgress(self.progress)
        self.download.start().addCallback(self.finished).addErrback(self.failed)
        self.downloading(True)
        self['fname'].text = _('Downloading file: %s ...') % self.filename

    def progress(self, recvbytes, totalbytes):
        if self.download:
            self['progressbar'].value = int(1000 * recvbytes / float(totalbytes))
            self['status'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def failed(self, failure_instance = None, error_message = ''):
        if error_message == '' and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
        if fileExists(self.dstfilename):
            remove(self.dstfilename)
        self['fname'].text = _('Download file %s failed!') % self.filename
        self['status'].text = error_message
        self.EVENT_CURR = self.EVENT_KILLED
        self.downloading(False)
        return

    def finished(self, string = ''):
        if self.download:
            self.EVENT_CURR = self.EVENT_DONE
            self.downloading(False)
            self['oktext'].hide()
            self['fname'].text = _('Download file %s finished!') % self.filename
            self['status'].text = ''
            self.autoCloseTimer.start(200)

    def stop(self):
        if self.download:
            self.download.stop()
            self.downloading(False)
            if fileExists(self.dstfilename):
                remove(self.dstfilename)
            self.EVENT_CURR = self.EVENT_KILLED
            self['fname'].text = _('Downloading killed by user!')
            self['status'].text = _('Press OK to close window.')

    def cancel(self):
        if self.download == None:
            self.close(self.EVENT_CURR)
        return