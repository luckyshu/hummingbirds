from twitter import *
import json
import util 

access_token_key = "134833802-ihkTufX0SeExjQsgbWEzMJ5r2pdmYS0zHbGJj4Vs"
access_token_secret = "Dplvd2COtKhLlm1ZVH2K6y3PmTyA1AHdgueyzI5k"

consumer_key = "Jro5MtJIYDUX5wxXecEQw"
consumer_secret = "GzurezzzB5to1zwe7ghzORuoBgekD2NULj0Qubew"

# get top 10 trends by city
def getTwitterTrends(city):
    twitter = Twitter(auth=OAuth(access_token_key, access_token_secret, consumer_key, consumer_secret))
    woeid = util.getWoeid(city)
    trend_query = twitter.trends.place(_id = woeid)
    
    phrases = []
    for result in trend_query[0]['trends']:
        phrase = result['name'].encode('utf-8').strip()
        phrases.append(phrase)
    return phrases
