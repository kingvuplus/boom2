# Embedded file name: /usr/lib/enigma2/python/ItalySat/ItalysatWeatherSearch.py
import urllib2
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from enigma import eTimer
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.config import config
import os

def uniq(inlist):
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append(item)

    return uniques


def get_weather_from_yahoo(location):

    def Filtro(text):
        text = text.replace('{', '').replace('}', '').replace(']', '').replace('[', '').replace(',', '')
        return text

    Citta = Nazione = Regione = Provincia = Codice = '**'
    url = 'http://sugg.us.search.yahoo.net/gossip-gl-location/?appid=weather&output=sd1&lc=it-IT&command=%s' % location.replace(' ', '%20')
    handler = urllib2.urlopen(url)
    dom = handler.read()
    handler.close()
    list = []
    xx = Filtro(dom).split('"k":')
    for x in xx:
        if x.find('&c=') != -1:
            String = '%ct=' + x
            try:
                Citta = String.split('%ct=')[1].split('"d"')[0].replace('"', '').strip()
            except:
                pass

            try:
                Nazione = String.split('&c=')[1].split('&')[0].replace('"', '').strip()
            except:
                pass

            try:
                Regione = String.split('&s=')[1].split('&')[0].replace('"', '').strip()
            except:
                pass

            try:
                Provincia = String.split('&n=')[1].replace('"', '').strip()
            except:
                pass

            try:
                Codice = String.split('&woeid=')[1].split('&')[0].replace('"', '').strip()
            except:
                pass

            list.append((Citta + ' (' + Provincia + ')' + '   ' + Regione + '   ' + Nazione, Codice))

    return list


class WeatherList(Screen):
    skin = '\n\t<screen name="WeaterCity" position="center,center" size="800,400" title="WeatherCity" backgroundColor="#10101010">\n\t\t<widget name="myMenu" position="20,10" size="760,330" scrollbarMode="showOnDemand" itemHeight="30" transparent="1" />\n\t\t<ePixmap alphatest="blend" pixmap="skin_default/buttons/red.png" position="27,352" size="140,40" />\n\t\t<ePixmap alphatest="blend" pixmap="skin_default/buttons/green.png" position="254,352" size="140,40" />\n\t\t<widget name="key_red" font="Regular;22" halign="left" position="27,352" size="140,40" transparent="1" zPosition="1" />\n\t\t<widget name="key_green" font="Regular;22" halign="left" position="254,352" size="140,40" transparent="1" zPosition="1" />\n\t</screen>'

    def __init__(self, session, Location):
        self.session = session
        Screen.__init__(self, session)
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Save'))
        self.Location = Location
        self.List = []
        self['myMenu'] = MenuList(self.List)
        self.MenuStart()
        self['myActionMap'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.go,
         'green': self.go,
         'cancel': self.Cancel,
         'red': self.Cancel}, -1)

    def MenuStart(self):
        self.List = []
        try:
            for x in get_weather_from_yahoo(self.Location):
                if x[1] != '**':
                    self.List.append((x[0], x[1]))

        except:
            pass

        self.List.sort(key=lambda t: tuple(t[0][0].lower()))
        self['myMenu'].setList(uniq(self.List))

    def go(self):
        try:
            Location_id = self['myMenu'].l.getCurrentSelection()[1]
            Region_id = self['myMenu'].l.getCurrentSelection()[0]
        except:
            Location_id = False
            Region_id = False

        if Location_id and Region_id:
            if config.skin.primary_skin.value.startswith('MetrixHD'):
                config.plugins.MetrixWeather.woeid.setValue(str(Location_id))
                config.plugins.MetrixWeather.woeid.save()
            if config.skin.primary_skin.value.startswith('iDreamy'):
                iLocation = open('/usr/lib/enigma2/python/Plugins/Extensions/YahooWeather/Config/Location_id', 'w')
                iLocation.write(str(Location_id))
                iLocation.close()
                iRegion = open('/usr/lib/enigma2/python/Plugins/Extensions/YahooWeather/Config/Region_id', 'w')
                iRegion.write(str(Region_id))
                iRegion.close()
                os.system('rm /tmp/yweather.xml')
        self.close()

    def Cancel(self):
        self.close()


class WeatherSearch(Screen):

    def __init__(self, session):
        self.session = session
        self.EnterLocation = ''
        self.iTimer = eTimer()
        self.iTimer.stop()
        self.iTimer.callback.append(self.KeyBoard)
        self.iTimer.start(100, True)
        Screen.__init__(self, session)
        self['myActionMap'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.Cancel,
         'red': self.Cancel}, -1)

    def Cancel(self):
        self.close()

    def KeyBoard(self):
        self.session.openWithCallback(lambda x: self.VirtualKeyBoardCallback(x), VirtualKeyBoard, title=_('Enter Location:'), text=self.EnterLocation)

    def VirtualKeyBoardCallback(self, callback = None):
        if callback is not None and len(callback):
            self.EnterLocation = callback
            self.session.open(WeatherList, self.EnterLocation)
        self.close()
        return