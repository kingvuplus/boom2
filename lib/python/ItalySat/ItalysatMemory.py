# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatMemory.py
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfo
from Screens.About import About
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from os import system, remove as os_remove
from enigma import eConsoleAppContainer, eTimer
from ItalysatUtils import ItalysatGetSkinPath

def getUnit(val):
    if val >= 1073741824:
        return '%.1f%s' % (float(val) / 1073741824, ' TB')
    if val >= 1048576:
        return '%.1f%s' % (float(val) / 1048576, ' GB')
    return '%.1f%s' % (float(val) / 1024, ' MB')


def getSize(a, b, c):
    return (getUnit(a), getUnit(b), getUnit(c))


class ItalyMemoryPanel(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen flags="wfNoBorder" position="0,0" size="1280,720" title="Memory" backgroundColor="black">\n\t\t  <ePixmap alphatest="on" pixmap="skin_default/italy_icons/bg_spy.png" position="0,0" size="1280,720" zPosition="-1" transparent="1" />\n\t\t  <widget name="flashbar" position="580,130" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="flash1" position="397,121" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="flash2" position="580,99" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="cfbar" position="580,188" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="cf1" position="397,177" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="cf2" position="580,158" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="usbbar" position="580,253" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="usb1" position="397,243" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="usb2" position="580,224" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="hddbar" position="580,323" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="hdd1" position="397,313" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="hdd2" position="580,293" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="totbar" position="580,598" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="tot1" position="397,589" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="tot2" position="580,568" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="rambar" position="580,388" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="ram1" position="397,377" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="ram2" position="580,358" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="swapbar" position="580,450" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="swap1" position="397,440" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="swap2" position="580,419" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="totalbar" position="580,514" size="580,12" pixmap="skin_default/italy_icons/ledbar.png" borderWidth="2" borderColor="darkgrey" transparent="1" />\n\t\t  <widget name="total1" position="397,504" size="179,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="total2" position="580,483" size="580,30" font="Regular;18" valign="center" transparent="1" />\n\t\t  <widget name="bot1" size="40,40" position="139,125" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot2" size="40,40" position="255,125" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot3" size="40,40" position="301,125" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot4" size="40,40" position="94,229" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot5" size="40,40" position="140,229" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot6" size="40,40" position="255,229" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot7" size="40,40" position="300,229" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot8" size="40,40" position="92,338" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot9" size="40,40" position="138,338" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot10" size="40,40" position="255,338" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t  <widget name="bot11" size="40,40" position="301,338" zPosition="1" pixmap="skin_default/italy_icons/spy_gray.png" alphatest="on" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        labelList = [('flash1', ''),
         ('flash2', ''),
         ('cf1', _('Compact Flash:')),
         ('cf2', ''),
         ('usb1', _('Usb:')),
         ('usb2', ''),
         ('hdd1', _('Hard Disk:')),
         ('hdd2', ''),
         ('tot1', 'Not Found'),
         ('tot2', ''),
         ('ram1', 'Ram: '),
         ('ram2', ''),
         ('swap1', 'Swap: '),
         ('swap2', ''),
         ('total1', 'Total Memory: '),
         ('total2', '')]
        progrList = ['rambar',
         'swapbar',
         'totbar',
         'flashbar',
         'cfbar',
         'usbbar',
         'hddbar',
         'totalbar']
        self['bot1'] = Pixmap()
        self['bot2'] = Pixmap()
        self['bot3'] = Pixmap()
        self['bot4'] = Pixmap()
        self['bot5'] = Pixmap()
        self['bot6'] = Pixmap()
        self['bot7'] = Pixmap()
        self['bot8'] = Pixmap()
        self['bot9'] = Pixmap()
        self['bot10'] = Pixmap()
        self['bot11'] = Pixmap()
        for x in labelList:
            self[x[0]] = Label(x[1])

        for x in progrList:
            self[x] = ProgressBar()

        c = eConsoleAppContainer()
        c.execute('df > /tmp/.df.tmp && free > /tmp/.mem.tmp')
        del c
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.close,
         'back': self.close})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateList)
        self.activityTimer.start(10)
        self.onShown.append(self.setWindowTitle)

    def updateList(self):
        self.activityTimer.stop()
        self.writelist()
        self.getSpyes()

    def setWindowTitle(self):
        self.setTitle(_('ItalySat Memory'))

    def writelist(self):
        self.activityTimer.stop()
        fls = 0
        totb = 0
        cf = [0,
         0,
         0,
         0]
        usb = [0,
         0,
         0,
         0]
        hdd = [0,
         0,
         0,
         0]
        tot = [0,
         0,
         0,
         0,
         0]
        if fileExists('/tmp/.df.tmp'):
            f = open('/tmp/.df.tmp', 'r')
            for line in f.readlines():
                line = line.replace('part1', ' ')
                x = line.strip().split()
                if x[0] == '/dev/root' or x[0] == 'ubi0:rootfs':
                    fls = int(x[4].replace('%', ''))
                    s = getUnit(int(x[1]))
                    s = getSize(int(x[1]), int(x[2]), int(x[3]))
                    self['flash2'].setText('Internal Flash: %s  -  [In Use:] %s' % (s[0], x[4]))
                    self['flash1'].setText(_('[Flash:] %s  -  [Used:] %s  -  [Free:] %s') % (s[0], s[1], s[2]))
                elif x[len(x) - 1] == '/media/cf':
                    try:
                        cf[0] = int(x[4].replace('%', ''))
                        cf[1] = int(x[1])
                        cf[2] = int(x[2])
                        cf[3] = int(x[3])
                        s = getUnit(int(x[1]))
                        g = getSize(int(x[1]), int(x[2]), int(x[3]))
                        self['cf1'].setText('*CF: %s' % x[4])
                        self['cf2'].setText(_('[CF:] %s  -  [Used:] %s  -  [Free:] %s') % (g[0], g[1], g[2]))
                    except:
                        cf = [0,
                         0,
                         0,
                         0]

                elif x[len(x) - 1] == '/media/usb':
                    try:
                        usb[0] = int(x[4].replace('%', ''))
                        usb[1] = int(x[1])
                        usb[2] = int(x[2])
                        usb[3] = int(x[3])
                        s = getUnit(int(x[1]))
                        g = getSize(int(x[1]), int(x[2]), int(x[3]))
                        self['usb1'].setText('*USB: %s' % x[4])
                        self['usb2'].setText(_('[USB:] %s  -  [Used:] %s  -  [Free:] %s') % (g[0], g[1], g[2]))
                    except:
                        usb = [0,
                         0,
                         0,
                         0]

                elif x[len(x) - 1] == '/media/hdd':
                    try:
                        hdd[0] = int(x[4].replace('%', ''))
                        hdd[1] = int(x[1])
                        hdd[2] = int(x[2])
                        hdd[3] = int(x[3])
                        s = getUnit(int(x[1]))
                        g = getSize(int(x[1]), int(x[2]), int(x[3]))
                        self['hdd1'].setText('*HDD: %s' % x[4])
                        self['hdd2'].setText(_('[HDD:] %s  -  [Used:] %s  -  [Free:] %s') % (g[0], g[1], g[2]))
                    except:
                        hdd = [0,
                         0,
                         0,
                         0]

            f.close()
            tot[0] = cf[1] + usb[1] + hdd[1]
            tot[1] = cf[2] + usb[2] + hdd[2]
            tot[2] = cf[3] + usb[3] + hdd[3]
            if tot[0] > 100:
                tot[3] = tot[1] * 100 / tot[0]
            elif tot[0] > 100:
                tot[4] = tot[2] * 100 / tot[0]
            s = getSize(tot[0], tot[1], tot[2])
            self['tot1'].setText('Total Space: %s  -  [In Use:] %d%%' % (s[0], tot[3]))
            self['tot2'].setText(_('[Total:] %s  -  [Used:] %s  -  [Free:] %s') % (s[0], s[1], s[2]))
            self['flashbar'].setValue(fls)
            self['cfbar'].setValue(cf[0])
            self['usbbar'].setValue(usb[0])
            self['hddbar'].setValue(hdd[0])
            totb = int(tot[3])
            self['totbar'].setValue(totb)
            system('rm -f /tmp/.df.tmp')
        r = [0, 0, 0]
        ram = [0,
         0,
         0,
         0]
        swap = [0,
         0,
         0,
         0]
        total = [0,
         0,
         0,
         0]
        if fileExists('/tmp/.mem.tmp'):
            f = open('/tmp/.mem.tmp', 'r')
            for line in f.readlines():
                x = line.strip().split()
                if x[0] == 'Mem:':
                    try:
                        ram[1] = int(x[1])
                        ram[2] = int(x[2])
                        ram[3] = int(x[3])
                        r[0] = int(int(x[2]) * 100 / int(x[1]))
                        self['ram1'].setText('*Ram: %d%%' % r[0])
                        s = getSize(int(x[1]), int(x[2]), int(x[3]))
                        self['ram2'].setText(_('[Ram:] %s  -  [Used:] %s  -  [Free:] %s') % (s[0], s[1], s[2]))
                    except:
                        ram = [0,
                         0,
                         0,
                         0]

                elif x[0] == 'Swap:':
                    try:
                        swap[1] = int(x[1])
                        swap[2] = int(x[2])
                        swap[3] = int(x[3])
                        if int(x[1]) > 1:
                            r[1] = int(int(x[2]) * 100 / int(x[1]))
                            self['swap1'].setText('*Swap: %d%%' % r[1])
                            s = getSize(int(x[1]), int(x[2]), int(x[3]))
                            self['swap2'].setText(_('[Swap:] %s  -  [Used:] %s  -  [Free:] %s') % (s[0], s[1], s[2]))
                    except:
                        swap = [0,
                         0,
                         0,
                         0]

            f.close()
            total[0] = ram[1] + swap[1]
            total[1] = ram[2] + swap[2]
            total[2] = ram[3] + swap[3]
            if total[0] > 101:
                total[3] = total[1] * 100 / total[0]
            s = getSize(total[0], total[1], total[2])
            self['total1'].setText(_('[Total:] %s  -  [Used:] %s  -  [Free:] %s') % (s[0], s[1], s[2]))
            self['total2'].setText('Total Memory: %s  -  [In Use:] %d%%' % (s[0], total[3]))
            self['rambar'].setValue(r[0])
            self['swapbar'].setValue(r[1])
            self['totalbar'].setValue(total[3])
            system('rm -f /tmp/.mem.tmp')

    def getSpyes(self):
        self.activityTimer.stop()
        atelnet = False
        aftp = False
        avpn = False
        asamba = False
        anfs = False
        rc = system('ps x > /tmp/.spy.tmp')
        if fileExists('/etc/inetd.conf'):
            f = open('/etc/inetd.conf', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                if parts[0] == 'telnet':
                    atelnet = True
                if parts[0] == 'ftp':
                    aftp = True

            f.close()
        if fileExists('/tmp/.spy.tmp'):
            f = open('/tmp/.spy.tmp', 'r')
            for line in f.readlines():
                if line.find('/usr/sbin/openvpn') != -1:
                    avpn = True
                if line.find('smbd') != -1:
                    asamba = True
                if line.find('/usr/sbin/rpc.mountd') != -1:
                    anfs = True

            f.close()
            os_remove('/tmp/.spy.tmp')
        if atelnet == True:
            self['bot2'].hide()
        else:
            self['bot3'].hide()
        if aftp == True:
            self['bot4'].hide()
        else:
            self['bot5'].hide()
        if avpn == True:
            self['bot6'].hide()
        else:
            self['bot7'].hide()
        if asamba == True:
            self['bot8'].hide()
        else:
            self['bot9'].hide()
        if anfs == True:
            self['bot10'].hide()
        else:
            self['bot11'].hide()