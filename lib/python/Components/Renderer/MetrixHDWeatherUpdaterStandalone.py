# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/MetrixHDWeatherUpdaterStandalone.py
from Renderer import Renderer
from Components.VariableText import VariableText
import urllib2
from enigma import eLabel
from xml.dom.minidom import parseString
from Components.config import config, configfile
from threading import Timer

class MetrixHDWeatherUpdaterStandalone(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.test = '3'
        config.plugins.MetrixWeather.save()
        configfile.save()
        self.woeid = config.plugins.MetrixWeather.woeid.value
        self.timer = None
        self.startTimer()
        self.getWeather()
        return

    GUI_WIDGET = eLabel

    def __del__(self):
        if self.timer is not None:
            self.timer.cancel()
        return

    def startTimer(self):
        seconds = int(config.plugins.MetrixWeather.refreshInterval.value) * 60
        if seconds < 60:
            seconds = 300
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.timer = Timer(seconds, self.getWeather)
        self.timer.start()
        return

    def onShow(self):
        self.text = config.plugins.MetrixWeather.currentWeatherCode.value

    def getWeather(self):
        self.startTimer()
        print 'MetrixHDWeatherStandalone lookup for ID ' + str(self.woeid)
        url = 'http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22' + str(self.woeid) + '%22&format=xml'
        try:
            file = urllib2.urlopen(url, timeout=2)
            data = file.read()
            file.close()
        except Exception as error:
            print 'Cant get weather data: %r' % error
            return

        dom = parseString(data)
        title = self.getText(dom.getElementsByTagName('title')[0].childNodes)
        config.plugins.MetrixWeather.currentLocation.value = str(title).split(',')[0].replace('Conditions for ', '')
        currentWeather = dom.getElementsByTagName('yweather:condition')[0]
        currentWeatherCode = currentWeather.getAttributeNode('code')
        config.plugins.MetrixWeather.currentWeatherCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('temp')
        config.plugins.MetrixWeather.currentWeatherTemp.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherText = currentWeather.getAttributeNode('text')
        config.plugins.MetrixWeather.currentWeatherText.value = currentWeatherText.nodeValue
        currentWeather = dom.getElementsByTagName('yweather:forecast')[0]
        currentWeatherCode = currentWeather.getAttributeNode('code')
        config.plugins.MetrixWeather.forecastTodayCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('high')
        config.plugins.MetrixWeather.forecastTodayTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('low')
        config.plugins.MetrixWeather.forecastTodayTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherText = currentWeather.getAttributeNode('text')
        config.plugins.MetrixWeather.forecastTodayText.value = currentWeatherText.nodeValue
        currentWeather = dom.getElementsByTagName('yweather:forecast')[1]
        currentWeatherCode = currentWeather.getAttributeNode('code')
        config.plugins.MetrixWeather.forecastTomorrowCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('high')
        config.plugins.MetrixWeather.forecastTomorrowTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('low')
        config.plugins.MetrixWeather.forecastTomorrowTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherText = currentWeather.getAttributeNode('text')
        config.plugins.MetrixWeather.forecastTomorrowText.value = currentWeatherText.nodeValue

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)

        return ''.join(rc)

    def ConvertCondition(self, c):
        c = int(c)
        condition = '('
        if c == 0 or c == 1 or c == 2:
            condition = 'S'
        elif c == 3 or c == 4:
            condition = 'Z'
        elif c == 5 or c == 6 or c == 7 or c == 18:
            condition = 'U'
        elif c == 8 or c == 10 or c == 25:
            condition = 'G'
        elif c == 9:
            condition = 'Q'
        elif c == 11 or c == 12 or c == 40:
            condition = 'R'
        elif c == 13 or c == 14 or c == 15 or c == 16 or c == 41 or c == 46 or c == 42 or c == 43:
            condition = 'W'
        elif c == 17 or c == 35:
            condition = 'X'
        elif c == 19:
            condition = 'F'
        elif c == 20 or c == 21 or c == 22:
            condition = 'L'
        elif c == 23 or c == 24:
            condition = 'S'
        elif c == 26 or c == 44:
            condition = 'N'
        elif c == 27 or c == 29:
            condition = 'I'
        elif c == 28 or c == 30:
            condition = 'H'
        elif c == 31 or c == 33:
            condition = 'C'
        elif c == 32 or c == 34:
            condition = 'B'
        elif c == 36:
            condition = 'B'
        elif c == 37 or c == 38 or c == 39 or c == 45 or c == 47:
            condition = '0'
        else:
            condition = ')'
        return str(condition)

    def getTemp(self, temp):
        if config.plugins.MetrixWeather.tempUnit.value == 'Fahrenheit':
            return str(int(round(float(temp), 0)))
        else:
            celsius = (float(temp) - 32) * 5 / 9
            return str(int(round(float(celsius), 0)))