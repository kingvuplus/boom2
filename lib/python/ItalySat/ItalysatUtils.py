# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatUtils.py
from Components.config import config
from re import sub
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_CURRENT_SKIN
import xml.etree.cElementTree
entities = [('&#228;', u'\xe4'),
 ('&auml;', u'\xe4'),
 ('&#252;', u'\xfc'),
 ('&uuml;', u'\xfc'),
 ('&#246;', u'\xf6'),
 ('&ouml;', u'\xf6'),
 ('&#196;', u'\xc4'),
 ('&Auml;', u'\xc4'),
 ('&#220;', u'\xdc'),
 ('&Uuml;', u'\xdc'),
 ('&#214;', u'\xd6'),
 ('&Ouml;', u'\xd6'),
 ('&#223;', u'\xdf'),
 ('&szlig;', u'\xdf'),
 ('&#8230;', u'...'),
 ('&#8211;', u'-'),
 ('&#160;', u' '),
 ('&#34;', u'"'),
 ('&#38;', u'&'),
 ('&#39;', u"'"),
 ('&#60;', u'<'),
 ('&#62;', u'>'),
 ('&lt;', u'<'),
 ('&gt;', u'>'),
 ('&nbsp;', u' '),
 ('&amp;', u'&'),
 ('&quot;', u'"'),
 ('&apos;', u"'")]

def italysat_strip_html(html):
    html = html.replace('\n', ' ')
    html = sub('\\s\\s+', ' ', html)
    html = sub('<br(\\s+/)?>', '\n', html)
    html = sub('</?(p|ul|ol)(\\s+.*?)?>', '\n', html)
    html = sub('<li(\\s+.*?)?>', '-', html)
    html = html.replace('</li>', '\n')
    return italysat_strip_pass1(html)


def italysat_strip_pass1(html):
    html = sub('<(.*?)>', '', html)
    html.replace('&#196;', '\xc3\x84')
    html.replace('&#228;', '\xc3\xa4')
    html.replace('&auml;', '\xc3\xa4')
    html.replace('&#252;', '\xc3\xbc')
    html.replace('&uuml;', '\xc3\xbc')
    html.replace('&#246;', '\xc3\xb6')
    html.replace('&ouml;', '\xc3\xb6')
    html.replace('&#196;', '\xc3\x84')
    html.replace('&Auml;', '\xc3\x84')
    html.replace('&#220;', '\xc3\x9c')
    html.replace('&Uuml;', '\xc3\x9c')
    html.replace('&#214;', '\xc3\x96')
    html.replace('&Ouml;', '\xc3\x96')
    html.replace('&#223;', '\xc3\x9f')
    html.replace('&szlig;', '\xc3\x9f')
    html.replace('&lt;', '<')
    html.replace('&gt;', '>')
    html.replace('&nbsp;', ' ')
    html.replace('&amp;', '&')
    html.replace('&quot;', '"')
    html.replace('&apos;', "'")
    return html


def ItalysatGetSkinPath():
    myskinpath = resolveFilename(SCOPE_CURRENT_SKIN, '')
    myskinpath = '/usr/share/enigma2/skin_default/'
    return myskinpath


def italysat_get_Version():
    ver = '4.0'
    if fileExists('/etc/italyversion'):
        f = open('/etc/italyversion', 'r')
        ver = f.readline().strip()
        ver = ver.replace('ItalySat ', '')
        f.close()
    return ver


from Components.MenuList import MenuList
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
from Tools.HardwareInfo import HardwareInfo
from enigma import eListboxPythonMultiContent, eListbox, eTimer, gFont
from Components.config import config
from os import system, statvfs, remove
import os
from re import sub
import xml.etree.cElementTree

class ItalysatUtils:

    def readEmuName(self, emu):
        try:
            f = open('/usr/emuscript/' + emu + '_em.sh', 'r')
            for line in f.readlines():
                if line.find('#emuname=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
            return emu
        except:
            return 'None'

    def readSrvName(self, srv):
        try:
            f = open('/usr/emuscript/' + srv + '_cs.sh', 'r')
            for line in f.readlines():
                if line.find('#srvname=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
            return srv
        except:
            return 'None'

    def readEcmInfoFile(self, emu):
        try:
            f = open('/usr/emuscript/' + emu + '_em.sh', 'r')
            for line in f.readlines():
                if line.find('#ecminfofile=') >= 0:
                    f.close()
                    return '/tmp/' + line.split('=')[1][:-1]

            f.close()
        except:
            return '/tmp/ecm.info'

    def readEmuActive(self):
        try:
            f = open('/var/bin/emudefault', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'None'

    def readSrvActive(self):
        try:
            f = open('/var/bin/csdefault', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'None'

    def readPortNumber(self):
        try:
            f = open('/var/etc/italysat.cfg', 'r')
            for line in f.readlines():
                if line.find('daemon_port=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
        except:
            return '1888'

    def readAddonsUrl(self):
        try:
            f = open('/var/etc/addons.url', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'http://feeds.italysat.eu/'

    def readAddonsPers(self):
        try:
            f = open('/var/etc/it_personal.url', 'r')
            line = f.readline()[:-1]
            f.close()
            return line
        except:
            return None

        return None

    def readExtraUrl(self):
        try:
            f = open('/var/etc/it_extra.url', 'r')
            line = f.readline()[:-1]
            f.close()
            return line
        except:
            return None

        return None

    def readCloneUrl(self):
        try:
            f = open('/etc/dream', 'r')
            line = f.readline()[:-1]
            f.close()
            return line
        except:
            return None

        return None

    def getVarSpace(self):
        free = -1
        try:
            s = statvfs('/')
        except OSError:
            return free

        free = s.f_bfree / 1024 * s.f_bsize / 1024
        return s.f_bfree / 1024 * (s.f_bsize / 1024)

    def getVarSpaceKb(self):
        try:
            s = statvfs('/')
        except OSError:
            return (0, 0)

        return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))

    def readEcmInfo(self):
        emuActive = self.readEmuActive()
        info = parse_ecm(self.readEcmInfoFile(emuActive))
        if info != 0:
            caid = info[0]
            pid = info[1]
            provid = info[2]
            ecmtime = info[3]
            source = info[4]
            addr = info[5]
            port = info[6]
            hops = info[7]
            reader = info[8]
            protocol = info[9]
            cw0 = info[10]
            cw1 = info[11]
            returnMsg = ''
            if provid != '':
                returnMsg += 'Provider: ' + provid + '\n'
            if caid != '':
                returnMsg += 'Ca ID: ' + caid + '\n'
            if pid != '':
                returnMsg += 'Pid: ' + pid + '\n'
            if source == 0:
                returnMsg += 'Decode: Unsupported!\n'
            elif source == 1:
                returnMsg += 'Decode: Internal\n'
            elif source == 2:
                returnMsg += 'Decode: Network\n'
                if config.italysat.shownetdet.value:
                    if addr != '':
                        returnMsg += '  Source: ' + addr + '\n'
                    if port != '':
                        returnMsg += '  Port: ' + port + '\n'
                    if hops > 0:
                        returnMsg += '  Hops: ' + str(hops) + '\n'
                    if protocol != '':
                        returnMsg += '  Protocol: ' + protocol + '\n'
                    if reader != '':
                        returnMsg += '  Reader: ' + reader + '\n'
            elif source == 3:
                returnMsg += 'Decode: ' + reader + '\n'
            elif source == 4:
                returnMsg += 'Decode: slot-1\n'
            elif source == 5:
                returnMsg += 'Decode: slot-2\n'
            if ecmtime > 0:
                returnMsg += 'ECM Time: ' + str(ecmtime) + ' msec\n'
            if cw0 != '':
                returnMsg += 'cw0: ' + cw0 + '\n'
            if cw1 != '':
                returnMsg += 'cw1: ' + cw1 + '\n'
            return returnMsg
        else:
            return 'No Info'


def parse_ecm(filename):
    addr = caid = pid = provid = port = reader = protocol = cw0 = cw1 = ''
    source = ecmtime = hops = 0
    try:
        file = open(filename)
        for line in file.readlines():
            line = line.strip()
            if line.find('CaID') >= 0:
                x = line.split(' ')
                caid = x[x.index('CaID') + 1].split(',')[0].strip()
            elif line.find('caid') >= 0:
                x = line.split(':', 1)
                caid = x[1].strip()
            if line.find('pid:') >= 0:
                x = line.split(':', 1)
                pid = x[1].strip()
            elif line.find('pid') >= 0:
                x = line.split(' ')
                pid = x[x.index('pid') + 1].strip()
            if line.find('prov:') >= 0:
                x = line.split(':', 1)
                provid = x[1].strip().split(',')[0]
            elif line.find('provid:') >= 0:
                x = line.split(':', 1)
                provid = x[1].strip()
            if line.find('msec') >= 0:
                x = line.split(' ', 1)
                ecmtime = int(x[0].strip())
            elif line.find('ecm time:') >= 0:
                x = line.split(':', 1)
                if x[1].strip() == 'nan':
                    ecmtime = 0
                else:
                    try:
                        ecmtime = int(float(x[1].strip()) * 1000)
                    except:
                        y = x[1].strip().split(' ', 1)
                        ecmtime = int(float(y[0].strip()))

            if line.find('hops:') >= 0:
                x = line.split(':', 1)
                hops = int(x[1].strip())
            if line.find('reader:') >= 0:
                x = line.split(':', 1)
                reader = x[1].strip()
            if line.find('protocol:') >= 0:
                x = line.split(':', 1)
                protocol = x[1].strip()
            if line.find('using:') >= 0:
                x = line.split(':', 1)
                if x[1].strip() == 'emu':
                    source = 1
                elif x[1].strip() == 'net' or x[1].strip() == 'newcamd' or x[1].strip() == 'CCcam-s2s' or x[1].strip() == 'gbox':
                    source = 2
            elif line.find('source:') >= 0:
                x = line.split(':')
                if x[1].strip() == 'emu':
                    source = 1
                elif x[1].find('net') >= 0:
                    source = 2
                    port = x[2].strip().split(')')[0]
                    addr = x[1].split(' ')[4]
                elif x[1].strip() == 'newcamd':
                    source = 2
            elif line.find('address:') >= 0:
                x = line.split(':')
                if x[1].strip() != '':
                    if x[1].find('/dev/sci0') >= 0:
                        source = 4
                    elif x[1].find('/dev/sci1') >= 0:
                        source = 5
                    elif x[1].find('local') >= 0:
                        source = 1
                    elif x[1].find('/dev/ttyUSB0') >= 0:
                        source = 6
                    elif x[1].find('/dev/ttyUSB1') >= 0:
                        source = 7
                    else:
                        try:
                            addr = x[1].strip()
                            port = x[2].strip()
                        except:
                            addr = x[1].strip()

            elif line.find('from:') >= 0:
                if line.find('local') >= 0:
                    source = 3
                else:
                    source = 2
                    x = line.split(':')
                    addr = x[1].strip()
            elif line.find('slot-1') >= 0:
                source = 4
                if HardwareInfo().get_device_name() == 'dm800se':
                    source = 5
            elif line.find('slot-2') >= 0:
                source = 5
                if HardwareInfo().get_device_name() == 'dm800se':
                    source = 4
            elif line.find('decode:') >= 0:
                if line.find('Internal') >= 0:
                    source = 1
                elif line.find('Network') >= 0:
                    source = 2
                elif line.find('/dev/sci0') >= 0:
                    source = 4
                    if HardwareInfo().get_device_name() == 'dm800se':
                        source = 5
                elif line.find('/dev/sci1') >= 0:
                    source = 5
                    if HardwareInfo().get_device_name() == 'dm800se':
                        source = 4
                else:
                    source = 2
                    x = line.split(':')
                    if x[1].strip() != '':
                        try:
                            addr = x[1].strip()
                            port = x[2].strip()
                        except:
                            addr = x[1].strip()

            if line.find('cw0:') >= 0:
                x = line.split(':', 1)
                cw0 = x[1].strip()
            if line.find('cw1:') >= 0:
                x = line.split(':', 1)
                cw1 = x[1].strip()

        file.close()
        return (caid,
         pid,
         provid,
         ecmtime,
         source,
         addr,
         port,
         hops,
         reader,
         protocol,
         cw0,
         cw1)
    except:
        return 0


def createIpupdateConf():
    out = open('/etc/ipupdate.conf', 'w')
    out.write('service-type=' + config.ipupdate.system.value.strip() + '\n')
    out.write('user=' + config.ipupdate.user.value.strip() + ':' + config.ipupdate.password.value.strip() + '\n')
    out.write('host=' + config.ipupdate.alias.value.strip() + '\n')
    out.write('server=' + config.ipupdate.server.value.strip() + '\n')
    out.write('interface=eth0\n')
    out.write('quiet\n')
    out.write('period=' + str(config.ipupdate.period.value) + '\n')
    out.close()