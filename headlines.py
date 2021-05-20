from flask import Flask 
import feedparser
from flask import render_template, request
import json, urllib.request, urllib.parse
import datetime 
from flask import make_response



app = Flask(__name__)

RSS_FEEDS =  {'daily': 'https://dailynews.com/feed/', 
              'cnn': 'http://rss.cnn.com/rss/edition_world.rss',
              'fox': 'http://feeds.foxnews.com/foxnews/latest', 
              'iol': 'https://rss.iol.io/iol/news',
              'elmasry': 'https://www.almasryalyoum.com/rss/rssfeeds',
              'youm7': 'https://www.youm7.com/rss/SectionRss'}

DEFAULTS = {'publication': 'fox', 
            'city': 'Cairo, EG',
            'currency_from':'USD',
            'currency_to':'EGP'
            }

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q=cairo&units=metric&appid=8fc7a1e449b0e1af7286a3e73a704719'
CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=6db1009d91c9499e8601fe940f47f6e1'


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)

    if request.cookies.get(key):
        return request.cookies.get(key)

    return DEFAULTS[key]

@app.route('/')
def home():
    
    # get customized headlines, based on user input or default
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)
    
    # get customized weather based on user input or default 
    city = get_value_with_fallback('city')
    weather = get_weather(city)

    # get customized currency based on user input or default
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rate(currency_from, currency_to)

    # save cookies and return template
    response = make_response(render_template("home.html", articles=articles,
                                              weather=weather,
                                              currency_from=currency_from,
                                              currency_to=currency_to,
                                              rate=rate,
                                              currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currecy_to", currency_to, expires=expires)
    
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib.request.urlopen(WEATHER_URL).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {
            'description': parsed['weather'][0]['description'],
            'temperature': parsed['main']['temp'],
            'city': parsed['name'],
            'country': parsed['sys']['country']
        }
        
    return weather

def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()

    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())

    return (to_rate / frm_rate, parsed.keys())




if __name__=="__main__":
    app.run(debug=True)


