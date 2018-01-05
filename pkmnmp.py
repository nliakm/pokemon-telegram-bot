#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import datetime
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import emoji

# list that stores the IDs of already scanned pokemon
encounter_ids = []
global_counter = 0
# logger for telegram-bot
logger = logging.getLogger(__name__)
# create a requests session
s = requests.Session()
genderType = [':no_entry_sign:', ':mens:', ':womens:']
wather_condition = ['', '', 'teilweise bewoelkt']


class PokemonScanner:

    #----------------------------------------------------------------------
    def getToken(self, url):
        """Do the initial request with selenium to store the needed token for further requests"""

        global token
        global s

        # initialize selenium browser
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        browser = webdriver.Chrome(
            '/home/akm/Downloads/Downloads/chromedriver', chrome_options=options)
        browser.get(url)
        time.sleep(1)

        # get token from source_code
        token = browser.find_element_by_xpath(
            "/html/head/script[3]").get_attribute("innerHTML")
        tokenSplit = token.split("'")
        token = tokenSplit[1]

        # transfer cookies from selenium to requests
        cookies = browser.get_cookies()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        print token

#----------------------------------------------------------------------
    def fillPokemonDict(self, pokemon, att, deff, sta):
        return -1

#----------------------------------------------------------------------
    def doRequest(self, url, att, deff, sta):
        """Get all displayed pokemon in chosen area"""

        # set headers
        headers = {
            'Origin': 'https://bs-pogo.de',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://bs-pogo.de/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        # configuration for scanning
        data = [
            ('timestamp', str(int(time.mktime(datetime.datetime.today().timetuple())))),
            ('pokemon', 'true'),
            ('lastpokemon', 'false'),
            ('pokestops', 'false'),
            ('lastpokestops', 'false'),
            ('luredonly', 'false'),
            ('gyms', 'false'),
            ('lastgyms', 'false'),
            ('scanned', 'true'),
            ('lastslocs', 'true'),
            ('spawnpoints', 'false'),
            ('lastspawns', 'true'),
            ('swLat', '52.242435307749346'),
            ('swLng', '10.276632876464873'),
            ('neLat', '52.36168192213934'),
            ('neLng', '10.853415103027373'),
            ('oSwLat', '52.242435307749346'),
            ('oSwLng', '10.276632876464873'),
            ('oNeLat', '52.36168192213934'),
            ('oNeLng', '10.853415103027373'),
            #('reids', ''),
            #('eids', ''),
            ('token', token),
        ]

        # empty dictionary to store the scanned pokemon
        pokemon_dict = {}

        # do the request that returns all pokemon at a certain area
        request_response = s.post(url, headers=headers, data=data)

        # try to get response (json) and request new token if exception is thrown (mostly due inactivity)
        try:
            json_response = request_response.json()
        except ValueError:
            self.getToken("https://bs-pogo.de/")
            time.sleep(3)
            request_response = s.post(url, headers=headers, data=data)
            json_response = request_response.json()

        for pokemon in json_response['pokemons']:
            # only store pokemon with minimum IVs or with specific ids
            if(pokemon['individual_attack'] > att and pokemon['individual_defense'] > deff and pokemon['individual_stamina'] > sta) or (pokemon['pokemon_id'] == 76 or pokemon['pokemon_id'] == 89 or pokemon['pokemon_id'] == 143 or pokemon['pokemon_id'] == 148 or pokemon['pokemon_id'] == 149 or pokemon['pokemon_id'] == 180 or pokemon['pokemon_id'] == 181 or pokemon['pokemon_id'] == 201 or pokemon['pokemon_id'] == 242 or pokemon['pokemon_id'] == 246 or pokemon['pokemon_id'] == 247 or pokemon['pokemon_id'] == 248 or pokemon['pokemon_id'] == 281 or pokemon['pokemon_id'] == 288 or pokemon['pokemon_id'] == 289 or pokemon['pokemon_id'] == 321 or pokemon['pokemon_id'] == 349 or pokemon['pokemon_id'] == 350):
                # disapper time of pokemon in milliseconds
                dt = pokemon['disappear_time']
                # convert milliseconds to date with time and store only the time
                disapper_time = str(time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(dt / 1000.0))).split(' ')[1]

                pkmn_longitude = ''
                pkmn_latitude = ''
                # store useful values from pokemon in variables

                if pokemon['level'] is None:
                    pkmn_level = 'N.A.'
                    iv_att = 'N.A.'
                    iv_def = 'N.A.'
                    iv_sta = 'N.A.'
                    pkmn_cp = 'N.A.'
                else:
                    pkmn_level = pokemon['level']
                    iv_att = str(pokemon['individual_attack'])
                    iv_def = str(pokemon['individual_defense'])
                    iv_sta = str(pokemon['individual_stamina'])
                    pkmn_cp = str(pokemon['cp'])

                pkmn_name = pokemon['pokemon_name']
                pkmn_longitude = str(pokemon['longitude'])
                pkmn_latitude = str(pokemon['latitude'])

                # no boost = 0, boost = 1
                pkmn_boosted = pokemon['weather_boosted_condition']
                pkmn_gender = pokemon['gender']
                pkmn_encounter_id = pokemon['encounter_id']

                # add new empty entry for dictionary with encounter_id as id
                pokemon_dict[pkmn_encounter_id] = {}

                # update created entry with values
                pokemon_dict[pkmn_encounter_id].update({
                    'cp': pkmn_cp,
                    'name': pkmn_name,
                    'level': pkmn_level,
                    'att': iv_att,
                    'deff': iv_def,
                    'sta': iv_sta,
                    'encounter_id': pkmn_encounter_id,
                    'longitude': pkmn_longitude,
                    'latitude': pkmn_latitude,
                    'disappear_time': disapper_time,
                    'weather_boost': pkmn_boosted,
                    'gender': pkmn_gender
                })
        print '############# Suche abgeschlossen #############'
        return pokemon_dict

#----------------------------------------------------------------------
    def scanSpecificPokemon(self, url, pokemon_id):
        global global_counter
        global encounter_ids

        # set headers
        headers = {
            'Origin': 'https://bs-pogo.de',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://bs-pogo.de/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        # configuration for scanning
        data = [
            ('timestamp', str(int(time.mktime(datetime.datetime.today().timetuple())))),
            ('pokemon', 'true'),
            ('lastpokemon', 'false'),
            ('pokestops', 'false'),
            ('lastpokestops', 'false'),
            ('luredonly', 'false'),
            ('gyms', 'false'),
            ('lastgyms', 'false'),
            ('scanned', 'true'),
            ('lastslocs', 'true'),
            ('spawnpoints', 'false'),
            ('lastspawns', 'true'),
            ('swLat', '52.242435307749346'),
            ('swLng', '10.276632876464873'),
            ('neLat', '52.36168192213934'),
            ('neLng', '10.853415103027373'),
            ('oSwLat', '52.242435307749346'),
            ('oSwLng', '10.276632876464873'),
            ('oNeLat', '52.36168192213934'),
            ('oNeLng', '10.853415103027373'),
            ('reids', str(pokemon_id)),
            #('eids', ''),
            ('token', token),
        ]

        # empty dictionary to store the scanned pokemon
        pokemon_dict = {}

        # do the request that returns all pokemon at a certain area
        request_response = s.post(url, headers=headers, data=data)

        # try to get response (json) and request new token if exception is thrown (mostly due inactivity)
        try:
            json_response = request_response.json()
        except ValueError:
            self.getToken("https://bs-pogo.de/")
            time.sleep(3)
            request_response = s.post(url, headers=headers, data=data)
            json_response = request_response.json()

        for pokemon in json_response['pokemons']:
            if str(pokemon['pokemon_id']) == pokemon_id:
                # disapper time of pokemon in milliseconds
                dt = pokemon['disappear_time']
                # convert milliseconds to date with time and store only the time
                disapper_time = str(time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(dt / 1000.0))).split(' ')[1]

                # store useful values from pokemon in variables
                if pokemon['level'] is None:
                    pkmn_level = 'N.A.'
                    iv_att = 'N.A.'
                    iv_def = 'N.A.'
                    iv_sta = 'N.A.'
                    pkmn_cp = 'N.A.'
                else:
                    pkmn_level = pokemon['level']
                    iv_att = str(pokemon['individual_attack'])
                    iv_def = str(pokemon['individual_defense'])
                    iv_sta = str(pokemon['individual_stamina'])
                    pkmn_cp = str(pokemon['cp'])
                pkmn_name = pokemon['pokemon_name']
                pkmn_longitude = str(pokemon['longitude'])
                pkmn_latitude = str(pokemon['latitude'])
                # no boost = 0, boost = 1
                pkmn_boosted = pokemon['weather_boosted_condition']
                pkmn_gender = pokemon['gender']
                pkmn_cp = str(pokemon['cp'])
                pkmn_encounter_id = pokemon['encounter_id']

                # add new empty entry for dictionary with encounter_id as id
                pokemon_dict[pkmn_encounter_id] = {}

                # update created entry with values
                pokemon_dict[pkmn_encounter_id].update({
                    'cp': pkmn_cp,
                    'name': pkmn_name,
                    'level': pkmn_level,
                    'att': iv_att,
                    'deff': iv_def,
                    'sta': iv_sta,
                    'encounter_id': pkmn_encounter_id,
                    'longitude': pkmn_longitude,
                    'latitude': pkmn_latitude,
                    'disappear_time': disapper_time,
                    'weather_boost': pkmn_boosted,
                    'gender': pkmn_gender
                })
        print '############# Suche nach ' + str(pokemon_id) + ' abgeschlossen #############'
        return pokemon_dict

#----------------------------------------------------------------------
    def scanLevel(self, url, pokemon_level):
        global global_counter
        global encounter_ids

        # set headers
        headers = {
            'Origin': 'https://bs-pogo.de',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://bs-pogo.de/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        # configuration for scanning
        data = [
            ('timestamp', str(int(time.mktime(datetime.datetime.today().timetuple())))),
            ('pokemon', 'true'),
            ('lastpokemon', 'false'),
            ('pokestops', 'false'),
            ('lastpokestops', 'false'),
            ('luredonly', 'false'),
            ('gyms', 'false'),
            ('lastgyms', 'false'),
            ('scanned', 'true'),
            ('lastslocs', 'true'),
            ('spawnpoints', 'false'),
            ('lastspawns', 'true'),
            ('swLat', '52.242435307749346'),
            ('swLng', '10.276632876464873'),
            ('neLat', '52.36168192213934'),
            ('neLng', '10.853415103027373'),
            ('oSwLat', '52.242435307749346'),
            ('oSwLng', '10.276632876464873'),
            ('oNeLat', '52.36168192213934'),
            ('oNeLng', '10.853415103027373'),
            ('reids', ''),
            #('reids', '10','11','13','14','16','17','19','21','41','161','163','165','167','177','183','187','194','206','223','263','309','325'),
            ('eids', ''),
            ('token', token),
        ]

        # empty dictionary to store the scanned pokemon
        pokemon_dict = {}

        # do the request that returns all pokemon at a certain area
        request_response = s.post(url, headers=headers, data=data)

        # try to get response (json) and request new token if exception is thrown (mostly due inactivity)
        try:
            json_response = request_response.json()
        except ValueError:
            self.getToken("https://bs-pogo.de/")
            time.sleep(3)
            request_response = s.post(url, headers=headers, data=data)
            json_response = request_response.json()

        for pokemon in json_response['pokemons']:
            if pokemon['level'] is not None and int(pokemon['level']) >= pokemon_level:
                # disapper time of pokemon in milliseconds
                dt = pokemon['disappear_time']
                # convert milliseconds to date with time and store only the time
                disapper_time = str(time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(dt / 1000.0))).split(' ')[1]

                # store useful values from pokemon in variables
                if pokemon['level'] is None:
                    pkmn_level = 'N.A.'
                    iv_att = 'N.A.'
                    iv_def = 'N.A.'
                    iv_sta = 'N.A.'
                    pkmn_cp = 'N.A.'
                else:
                    pkmn_level = pokemon['level']
                    iv_att = str(pokemon['individual_attack'])
                    iv_def = str(pokemon['individual_defense'])
                    iv_sta = str(pokemon['individual_stamina'])
                    pkmn_cp = str(pokemon['cp'])
                pkmn_name = pokemon['pokemon_name']
                pkmn_longitude = str(pokemon['longitude'])
                pkmn_latitude = str(pokemon['latitude'])
                # no boost = 0, boost = 1
                pkmn_boosted = pokemon['weather_boosted_condition']
                pkmn_gender = pokemon['gender']
                pkmn_cp = str(pokemon['cp'])
                pkmn_encounter_id = pokemon['encounter_id']

                # add new empty entry for dictionary with encounter_id as id
                pokemon_dict[pkmn_encounter_id] = {}

                # update created entry with values
                pokemon_dict[pkmn_encounter_id].update({
                    'cp': pkmn_cp,
                    'name': pkmn_name,
                    'level': pkmn_level,
                    'att': iv_att,
                    'deff': iv_def,
                    'sta': iv_sta,
                    'encounter_id': pkmn_encounter_id,
                    'longitude': pkmn_longitude,
                    'latitude': pkmn_latitude,
                    'disappear_time': disapper_time,
                    'weather_boost': pkmn_boosted,
                    'gender': pkmn_gender
                })
        print '############# Suche nach min. Level ' + str(pokemon_level) + ' abgeschlossen #############'
        return pokemon_dict

class TelegramBot:
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)


#----------------------------------------------------------------------
    def customizeOutput(self, item):
        """customize the output message that will be send by the bot."""

        # set emoji for perfect iv pokemon
        if item['att'] == '15' and item['deff'] == '15' and item['sta'] == '15':
            iv_value = emoji.emojize(
                'Perfekte IVs! :100:', use_aliases=True)
        else:
            iv_value = 'Att: ' + \
                item['att'] + ', Def: ' + \
                item['deff'] + ', Sta: ' + item['sta']

        output = ''
        output = emoji.emojize(genderType[int(item['gender'])], use_aliases=True) + ' ' + str(item['name']) + \
            '\nLevel: ' + item['level'] + ', WP: ' + item['cp'] + \
            '\nIV: ' + iv_value + emoji.emojize('\n:clock4: ', use_aliases=True) + item['disappear_time'] + \
            emoji.emojize('\n:earth_africa: ', use_aliases=True) + \
            str(item['latitude']) + ',' + str(item['longitude'])

        return output

#----------------------------------------------------------------------
    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi {}!\nIch bin ein Scannerbot.\nSende /help für mehr Informationen.'.format(
            update.message.from_user.first_name),)

#----------------------------------------------------------------------
    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text(
            'Ich zeige Dir alle Pokemon mit sehr guten IV-Werten, sowie besondere Pokemon unabhängig von ihren Werten an.\nSende /scan um die Pokemon mitsamt Koordinaten anzeigen zu lassen.\nPer /show pokemon_id kannst Du Dir alle Pokemon mit der jeweiligen ID anzeigen lassen.')

#----------------------------------------------------------------------
    def show(self, bot, update):
        """shows specific pokemon"""
        pokemon_id = str(update.message.text).split(' ')[1]
        pokemonDict = pkmnscnnr.scanSpecificPokemon(
            'https://bs-pogo.de/raw_data', pokemon_id)
        if len(pokemonDict) == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Kein Pokemon mit ID ' + pokemon_id + ' gefunden!')
        else:
            for item in pokemonDict.values():
                bot.send_message(chat_id=update.message.chat_id,
                                 text=self.customizeOutput(item))
                time.sleep(0.1)

#----------------------------------------------------------------------
    def scan(self, bot, update):
        """executes request and respond all scanned pokemon with chosen IVs in an area when a user messages /scan"""

        # get scanned pokemon and store them in a dictionary
        pokemonDict = pkmnscnnr.doRequest(
            "https://bs-pogo.de/raw_data", 14, 13, 13)
        output = ''
        # print len(pokemonDict)
        for item in pokemonDict.values():
            bot.send_message(chat_id=update.message.chat_id,
                             text=self.customizeOutput(item))
            time.sleep(0.1)

#----------------------------------------------------------------------
    def level(self, bot, update):
        """executes request and respond all scanned pokemon with chosen level when a user messages /level pokemon_level"""
        pokemon_level = str(update.message.text).split(' ')[1]
        pokemonDict = pkmnscnnr.scanLevel(
            'https://bs-pogo.de/raw_data', int(pokemon_level))
        if len(pokemonDict) == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Kein Pokemon mit Level ' + pokemon_level + ' oder höher gefunden!')
        else:
            for item in pokemonDict.values():
                bot.send_message(chat_id=update.message.chat_id,
                                 text=self.customizeOutput(item))
                time.sleep(0.1)


#----------------------------------------------------------------------
    def echo(self, bot, update):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

#----------------------------------------------------------------------
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        global logger
        logger.warning('Update "%s" caused error "%s"', update, error)

#----------------------------------------------------------------------
    def main(self):
        """Start the bot."""
        # Create the EventHandler and pass it your bot's token.
        updater = Updater("548102564:AAEjNNkQksJ2x65g9Ik_eEBgeI8vrBXMleQ")

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("scan", self.scan))
        dp.add_handler(CommandHandler("show", self.show))
        dp.add_handler(CommandHandler("level", self.level))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.echo))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


#----------------------------------------------------------------------
if __name__ == "__main__":
    pkmnscnnr = PokemonScanner()
    pkmnscnnr.getToken("https://bs-pogo.de/")
    #pkmnscnnr.doRequest("https://bs-pogo.de/raw_data", 14, 13, 13)
    tlgrmbt = TelegramBot()
    tlgrmbt.main()
