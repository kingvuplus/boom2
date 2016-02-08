# Embedded file name: /usr/lib/enigma2/python/Components/Converter/MetrixWeather.py
from Components.Converter.Converter import Converter
from Components.config import config, ConfigText, ConfigNumber, ConfigDateTime
from Components.Element import cached

class MetrixWeather(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)
        self.type = type

    @cached
    def getText(self):
        try:
            if self.type == 'currentLocation':
                return config.plugins.MetrixWeather.currentLocation.value
            if self.type == 'currentWeatherTemp':
                return config.plugins.MetrixWeather.currentWeatherTemp.value
            if self.type == 'currentWeatherText':
                return config.plugins.MetrixWeather.currentWeatherText.value
            if self.type == 'currentWeatherCode':
                return config.plugins.MetrixWeather.currentWeatherCode.value
            if self.type == 'forecastTodayCode':
                return config.plugins.MetrixWeather.forecastTodayCode.value
            if self.type == 'forecastTodayTempMin':
                return config.plugins.MetrixWeather.forecastTodayTempMin.value + ' ' + self.getCF()
            if self.type == 'forecastTodayTempMax':
                return config.plugins.MetrixWeather.forecastTodayTempMax.value + ' ' + self.getCF()
            if self.type == 'forecastTodayText':
                return config.plugins.MetrixWeather.forecastTodayText.value
            if self.type == 'forecastTomorrowCode':
                return config.plugins.MetrixWeather.forecastTomorrowCode.value
            if self.type == 'forecastTomorrowTempMin':
                return config.plugins.MetrixWeather.forecastTomorrowTempMin.value + ' ' + self.getCF()
            if self.type == 'forecastTomorrowTempMax':
                return config.plugins.MetrixWeather.forecastTomorrowTempMax.value + ' ' + self.getCF()
            if self.type == 'forecastTomorrowText':
                return config.plugins.MetrixWeather.forecastTomorrowText.value
            if self.type == 'title':
                return self.getCF() + ' | ' + config.plugins.MetrixWeather.currentLocation.value
            if self.type == 'CF':
                return self.getCF()
            return ''
        except:
            return ''

    def getCF(self):
        if config.plugins.MetrixWeather.tempUnit.value == 'Fahrenheit':
            return '\xc2\xb0F'
        else:
            return '\xc2\xb0C'

    text = property(getText)