import os
import re
import difflib
import goose
import nltk

stopwords = nltk.corpus.stopwords.words('english')
citymapping = 'citymapping.csv'

def getWoeid(city):
    cwd = os.path.dirname(os.path.abspath(__file__))
    ofile = open(os.path.join(cwd, citymapping), 'r')
    for line in ofile:
        l = line.split(';')
        if (l[0] == city):
            return l[1]
    ofile.close()
    """
    if city is not in the csv file, return woeid of USA
    """
    return 23424977

def getGeo(city):
    cwd = os.path.dirname(os.path.abspath(__file__))
    ofile = open(os.path.join(cwd, citymapping), 'r')
    for line in ofile:
        l = line.split(';')
        if (l[0] == city):
            return l[2]
    ofile.close()
    return '37.090240,-95.712891,3000km'


"""
format trend: "#DumbAndDumber" will be "Dumb And Dumber"
"""
def formatPhrase(phrase):
    phrase = phrase.replace('#', '')
    l = re.findall('[A-Z][^0-9A-Z]*|\d+[^A-Z]*', phrase)
    if (len(l) > 0):
        phrase = ' '.join(l)
    return phrase

"""
check similarity of tweets/news
"""
def checkUnique(text, l):
    if text is None:
        return False
    list_text = [ch for ch in text if ch.isalnum() or ch == ' ']
    for s in l:
        list_s = [ch for ch in s if ch.isalnum() or ch == ' ']
        sm = difflib.SequenceMatcher(None, list_text, list_s)
        if (sm.ratio() > 0.7):
            return False
    return True

"""
check whether the title of news is related to trend phrase or not
l is the list of words in trend
"""
def checkRelated(link, l, keywords):
    try:
        g = goose.Goose()
        article = g.extract(url=link)
        title = article.title
        meta = article.meta_description[:150]
        text = article.cleaned_text[:150]
        if title is None or text is None or title == '' or text == '':
            return False
        p = re.compile('(@[A-Za-z0-9_]+)|([^0-9A-Za-z \&\t])|(\w+:\/\/\S+)')
        title = re.sub(p, '', title)
        title_l = title.split(' ')
        meta = re.sub(p, '', meta)
        meta_l = meta.split(' ')
        text = re.sub(p, '', text)
        text_l = text.split(' ')
        news_l = []
        news_l.extend(title_l)
        news_l.extend(meta_l)
        news_l.extend(text_l)
        phrase_l = []
        phrase_l.extend(l)
        phrase_l.extend(keywords)
        
        count = 0
        if len(l) == 1:
            threshold = 2
        else:
            threshold = len(l) 
        news_lower_l = [word.lower() for word in news_l]
        for word in phrase_l:
            if str(word) in news_lower_l and word not in stopwords:
                count += 1
        if count >= threshold + 1:
            print link, 'True'
            return True
        else:
            print link, 'False'
            return False

    except:
        return False
