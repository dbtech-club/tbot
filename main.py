import argparse
from collections import namedtuple
from datetime import datetime
import logging

from pytz import timezone
import requests
import six.moves.urllib as urllib
from telegram.ext import Updater, CommandHandler
import yaml

GOOGLE_GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}'
GOOGLE_TIMEZONE_URL = 'https://maps.googleapis.com/maps/api/timezone/json?key={}&location={}&timestamp={}'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG = logging.getLogger(__name__)

SECRETS = None


def google_geocoding(location):
    url = GOOGLE_GEOCODING_URL.format(SECRETS.GOOGLE_API_KEY, urllib.parse.quote_plus(location))
    LOG.info('Google geocoding url: %s', url)
    resp = requests.get(url).json()
    coordinates = resp['results'][0]['geometry']['location']
    address = resp['results'][0]['formatted_address']
    return {'address': address, 'lat': coordinates['lat'], 'lng': coordinates['lng']}


def google_timezone(lat, lng):
    location = '{},{}'.format(lat, lng)
    url = GOOGLE_TIMEZONE_URL.format(SECRETS.GOOGLE_API_KEY, location, int(datetime.now(timezone('UTC')).strftime('%s')))
    resp = requests.get(url).json()
    return resp['timeZoneId']


def timeat(update, context):
    location = ','.join(context.args)
    LOG.info('Getting coordinates for the location %s', location)
    geocoding_result = google_geocoding(location)
    tzname = google_timezone(geocoding_result['lat'], geocoding_result['lng'])
    update.message.reply_text('Current time at {} is {}'.format(
        geocoding_result['address'], datetime.now(timezone(tzname)).strftime('%Y-%m-%d %H:%M:%S')))


def main():
    global SECRETS
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-file', required=True)
    args, _ = parser.parse_known_args()

    with open(args.secret_file) as f:
        secrets_data = yaml.safe_load(f)
        SECRETS = namedtuple('Secrets', secrets_data.keys())(*secrets_data.values())

    updater = Updater(SECRETS.TELEGRAM_BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('timeat', timeat))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
