from datetime import datetime
from pytz import timezone
import time
import logging
import requests
import yaml
import argparse
from telegram.ext import Updater, CommandHandler

GOOGLE_API_KEY = None
BASE_GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode/json?key={0}&address={1}'
BASE_TIMEZONE_URL = 'https://maps.googleapis.com/maps/api/timezone/json?key={0}&location={1}&timestamp={2}'

logging.basicConfig(level=logging.DEBUG)

def hello(update, context):
    update.message.reply_text("Hello, " + update.message.from_user.first_name)

def current_time(update, context):
    cur_price = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update.message.reply_text("Current time is: " + cur_price)

def google_geocoding(location):
    url = BASE_GEOCODING_URL.format(GOOGLE_API_KEY, location)
    response = requests.get(url).json()
    coordinates = response['results'][0]['geometry']['location']
    full_address = response['results'][0]['formatted_address']
    return {'full_address': full_address, 'lat': coordinates['lat'], 'lng': coordinates['lng']}

def google_timezone(lat, lng):
    location = '{},{}'.format(lat, lng)
    timestamp = int(time.mktime(datetime.now(timezone('UTC')).timetuple()))
    url = BASE_TIMEZONE_URL.format(GOOGLE_API_KEY, location, timestamp)
    resp = requests.get(url).json()
    return resp['timeZoneId']

def time_at(update, context):
    location = ','.join(context.args)
    geocoding_result = google_geocoding(location)
    tzname = google_timezone(geocoding_result['lat'], geocoding_result['lng'])
    update.message.reply_text('Current time at {} is {}'.format(
        geocoding_result['full_address'], datetime.now(timezone(tzname)).strftime('%Y-%m-%d %H:%M:%S')))


parser = argparse.ArgumentParser()
parser.add_argument('--secret', required=True)
args, _ = parser.parse_known_args()

with open(args.secret) as f:
    data = yaml.safe_load(f)

GOOGLE_API_KEY = data['GOOGLE_API_KEY']

updater = Updater(token=data['TELEGRAM_BOT_TOKEN'], use_context=True)
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('time', current_time))
updater.dispatcher.add_handler(CommandHandler('timeat', time_at))
updater.start_polling()
updater.idle()
