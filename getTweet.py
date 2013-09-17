from twitter import *
import sys
import calendar
import time
import re
import util 
import getSentiment

access_token_key = "134833802-ihkTufX0SeExjQsgbWEzMJ5r2pdmYS0zHbGJj4Vs"
access_token_secret = "Dplvd2COtKhLlm1ZVH2K6y3PmTyA1AHdgueyzI5k"

consumer_key = "Jro5MtJIYDUX5wxXecEQw"
consumer_secret = "GzurezzzB5to1zwe7ghzORuoBgekD2NULj0Qubew"

def getTweets(city, trend):
    twitter = Twitter(auth=OAuth(access_token_key, access_token_secret, consumer_key, consumer_secret))
    geocode = util.getGeo(city)
    query = twitter.search.tweets(q = trend, lang = 'en', count = 100, geocode = geocode)

    l = []
    prev_name = 'ls'
    text_l = []

    for result in query['statuses']:
        d = {}
        if result['retweeted'] == True:
            continue
        #parse the text of tweet
        text = result['text'].encode('utf-8').strip()
        if text == trend:
            continue
        p = re.compile('(@[A-Za-z0-9_]+)|([^0-9A-Za-z \#\t])|(\w+:\/\/\S+)')
        text = re.sub(p, '', text)

        if (text == trend):
            continue
        if (text.lower().find('rt') != -1):
            continue
        if (text.find('\xf0') != -1):
            continue 
        if not util.checkUnique(text, text_l):
            continue
        d['text'] = text

        #parse text of tweet without "#" for keywords counting
        p=re.compile('(@[A-Za-z0-9_]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)')
        text = re.sub(p, '', text)
        text_l.append(text)

        #parse user name of tweet
        d['name'] = result['user']['name'].encode('utf-8').strip()
        if d['name'] == prev_name:
            continue
        prev_name = d['name']
        if trend.find('#') != -1:
            trend = util.formatPhrase(trend)
        trend_l = trend.split(' ')
        name_l = d['name'].split(' ')
        for name in name_l:
            if name.title() in trend_l:
                continue

        #parse user location
        d['location'] = result['user']['location'].strip()

        #parse create time of tweet
        timestamp = result['created_at']
        format = '%a %b %d %H:%M:%S +0000 %Y'
        s = time.strptime(timestamp, format)
        d['created_at'] = int(calendar.timegm(s))
        
        #parse first url in tweet
        urls = result['entities']['urls']
        d['url'] = None
        if len(urls) > 0:
            d['url'] = urls[0]['expanded_url']
        l.append(d)
   
    # get sentiment of tweets
    getSentiment.getSentiments(l)

    # get top 10 frequent words of tweets
    keywords = getSentiment.getKeywords(trend, text_l)
    l.insert(0, keywords)

    return l
