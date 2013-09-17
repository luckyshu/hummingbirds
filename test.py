import getTweet
import getNews
import sys

def test(phrase):
    l = getTweet.getTweets('United States', phrase)
    getNews.getLinks(phrase, l)
