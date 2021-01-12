#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3

# <bitbar.title>CO2Signal API</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Martin Jobke</bitbar.author>
# <bitbar.author.github>pygoner</bitbar.author.github>
# <bitbar.desc>This plugin displays the current carbon (gC02equivalent) emmissions per kWh of produced electric energy in the requested country/region </bitbar.desc>
# <bitbar.dependencies>python, CO2 Signal</bitbar.dependencies>
# <bitbar.abouturl>https://docs.co2signal.com/</bitbar.abouturl>


import requests
import sys

# user settings 
# get your C02Signal API token at https://www.co2signal.com/
# insert your specific country code from this list http://api.electricitymap.org/v3/zones
# have fun ^^

myapitoken = ''
myCountrycode = ''

class CO2Signal:

    def __init__(self, authToken, countryCode):
        self.authToken = authToken
        self.countryCode = countryCode

    def requestC02Signal(self):
        url = 'http://api.co2signal.com/v1/latest?countryCode=' + self.countryCode
        headers = {'auth-token': self.authToken}
        self.resDict = requests.get(url, params=headers).json()

    def displayResponse(self):
        try:
            print(self.resDict['error'])
            self.dropdownMenu('', 'error')
            return
        except KeyError:
            stringToDisplay = self.countryFlag(self.countryCode)
            try:
                self.resDict['message']
                # if the API key is used more than 30 times an hour or wrong
                # the CO2 Signal return just a json containing 'message'
                self.dropdownMenu(stringToDisplay, 'APILimit')
                return
            except KeyError:
                # if the country live data is currently unavialable the
                # fossilFuelPercentage is null/none
                if (self.resDict['data']['fossilFuelPercentage']):
                    stringToDisplay += str(round(self.resDict['data']['carbonIntensity'], 1))
                    stringToDisplay += ' | color=' + self.color(self.resDict['data']['carbonIntensity'])
                    self.dropdownMenu(stringToDisplay, 'normal')
                else:
                    stringToDisplay += ':-( | color=#e62e00'     # red sad smiley
                    self.dropdownMenu(stringToDisplay, 'noLiveData')

    def dropdownMenu(self, stringToDisplay, mode):
        print(stringToDisplay)
        if (mode == 'normal'):
            print('---')
            ffp = round(self.resDict['data']['fossilFuelPercentage'], 1)
            # creating a smiley face which reflects the mood of
            # an environmental caring person ^^
            if (ffp < 20):
                ffp = str(ffp) + ' :heart_eyes:'
            else:
                if(ffp < 30):
                    ffp = ffp = str(ffp) + ' :grinning:'
                else:
                    if(ffp < 50):
                        ffp = ffp = str(ffp) + ' :neutral_face:'
                    else:
                        ffp = ffp = str(ffp) + ' :poop:'
            print('fossil fuel percentage: ' + ffp)
            print('-- percentage of electricity')
            print('-- generated by coal, gas or oil')
        
        if (mode == 'APILimit'):
            print('---')
            print(self.resDict['message'])
            if ('Invalid' in self.resDict['message']):
                print('Get a API key at https://www.co2signal.com/')

        if (mode == 'noLiveData'):
            print('---')
            print('No data currently avialable!')

        if (mode == 'error'):
            print('---')

        print('API Website (CO2 Signal)| href=https://www.co2signal.com/')
        print('electricityMap Website | href=https://electricitymap.org') 

    def countryFlag(self, countryCode='WhiteFlag'):
        # https://www.unicode.org/charts/PDF/U1F100.pdf
        # see regional indicator symbols
        if (countryCode == 'WhiteFlag'):
            return '🏳 '
        start = 0x1F1E6
        # unicode start for letter 'A' in regional Symbols
        letterOffset1 = ord(countryCode[0]) - ord('A')
        letterOffset2 = ord(countryCode[1]) - ord('A')
        # calculation of number which is added
        # e.g. 'D' as regional letter = 'A' as regional letter + 3
        letter1 = start + letterOffset1
        letter2 = start + letterOffset2
        return (chr(letter1) + chr(letter2))

    def rgb_to_hex(self, rgb):
        # https://www.codespeedy.com/convert-rgb-to-hex-color-code-in-python/
        return '%02x%02x%02x' % rgb

    def linearGradient(self, col1, col2, splitFactor):
        # this function returns the color which is in between those two colors and
        # is splits those two colors according to the split factor
        # e.g. col1 = (0, 0, 0); col2 = (40, 60, 80); SF = 0.4
        # linearGradient(col1, col2, SF) -> 0.4*((40, 60, 80) - (0, 0, 0))
        # similar to finding a point on straight between two points
        dif = (col1[0] - col2[0], col1[1] - col2[1], col1[2] - col2[2])
        dif = (dif[0]*splitFactor, dif[1]*splitFactor, dif[2]*splitFactor)
        result = (col1[0] - dif[0], col1[1] - dif[1], col1[2] - dif[2])
        result = (int(result[0]), int(result[1]), int(result[2]))
        return result
     
    def color(self, carbonIntensity):
        # this function should determine a color given the carbon intensity
        # low intensity -> more green
        # middle intensity -> yellow
        # high intensity -> brown
        # similar to the color scale at: electricitymap.org

        maximum = 800
        ratio = carbonIntensity / maximum

        colors = ((42, 163, 100), (162, 206, 86), (240, 225, 75),
                (222, 191, 68), (205, 158, 61), (188, 124, 53),
                (171, 91, 46), (143, 61, 35), (82, 39, 12), (56, 29, 2))
        splitLenght = 1 / 9

        # the color scale is split up nine times
        # each time there is a linear gradient betwenn the colors of the colors tuple

        k = int(ratio // splitLenght)
        splitFactor = (ratio % splitLenght) / splitLenght
        if (ratio >= 0.999999):
            return('#' + self.rgb_to_hex(colors[10]))
        else:
            carbonColor = self.linearGradient(colors[k], colors[k+1], splitFactor)
            carbonColor = self.rgb_to_hex(carbonColor)
            return('#' + carbonColor)


myCO2Signal = CO2Signal(myapitoken, myCountrycode)
myCO2Signal.requestC02Signal()
myCO2Signal.displayResponse()