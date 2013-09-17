import re
import nltk
import os
import operator
import util

stopwords = nltk.corpus.stopwords.words('english')
sent_file = 'AFINN-111.txt'

def read_sent():
    cwd = os.path.dirname(os.path.abspath(__file__))
    of = open(os.path.join(cwd, sent_file), 'r')
    scores = {}
    for line in of:
        word, score = line.strip().split('\t')
        scores[word] = int(score)
    of.close()
    return scores

def getSentiment(scores, tweet):
    sentiment = 0
    p=re.compile('(@[A-Za-z0-9_]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)')
    tweet = re.sub(p, '', tweet)
    words = tweet.split(' ')
    for word in words:
        word = word.lower()
        if word in scores:
            sentiment += scores[word]
    return sentiment

def getSentiments(l):
    scores = read_sent()
    for d in l:
        tweet = d['text']
        d['sentiment'] = getSentiment(scores, tweet)
    return l

def get_words_in_tweets(tweets):
    all_words = []
    for words in tweets:
        all_words.extend(words)
    return all_words

def get_top(trend, wordlist):
    d = {}
    wordlist = nltk.FreqDist(wordlist)
    sorted_words = sorted(wordlist.iteritems(), key = operator.itemgetter(1), reverse = True)
    i = 0
    if trend.find('#') != -1:
        trend = util.formatPhrase(trend)
    l = trend.split(' ')
    lower_l = [word.lower() for word in l]

    for word,frequency in sorted_words:
        if not word.isdigit() and word not in lower_l and word != ''.join(lower_l):
            d[word.lower()] = frequency 
            i += 1
        if i == 10:
            break
    return d

"""
remove stopwords in tweets
"""
def getfilteredTweets(tweets):
    tweets_filtered = []
    for tweet in tweets:
        words = tweet.split()
        words_filtered = [w.lower() for w in words if w.lower() not in stopwords]
        tweets_filtered.append(words_filtered)   
    return tweets_filtered

def getKeywords(trend, tweets):
    tweets_filtered = getfilteredTweets(tweets)
    return get_top(trend, get_words_in_tweets(tweets_filtered))
