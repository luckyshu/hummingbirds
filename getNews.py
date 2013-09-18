import requests
import json
import util
import goose
import time
import sys

linkClicksUrl = 'https://api-ssl.bitly.com/v3/link/clicks?access_token={0}&link={1}'

searchUrl = "https://api-ssl.bitly.com/v3/search?access_token={0}&query={1}&limit={2}&lang=en&fields=aggregate_link%2Ctitle"
link_limit = 5

categoryUrl = 'https://api-ssl.bitly.com/v3/link/category?access_token={0}&link={1}'

token = '900ec1b80e3a44d65daebc12acf830d2a415cf79'


def getClicks(link):
    r = requests.get(linkClicksUrl.format(token, link))
    response = json.loads(r.content)
    if (response['status_code'] == 200):
        return response['data']['link_clicks']
    elif (response['status_code'] == 404):
        return 0
    else:
        print 'getNews/getClicks', response['status_code']
        sys.exit(1)

def getLinks(phrase, l):
    keywords = l[0].keys()
    #gether keywords and links in tweets of trend
    tweet_links = []
    for d in l[1:]:
        if d['url'] is not None:
            tweet_links.append(d['url'])

    if phrase.find('#') != -1:
        phrase = util.formatPhrase(phrase)
   
    #if trend phrase is too long, only use the first three words
    list = [word.lower() for word in phrase.split(' ')]

    links = {}
    #add tweet links if it is a piece of news
    for link in tweet_links:
        if link.find('vine') != -1 or link.find('youtu') != -1 or link.find('instagram') != -1 or link.find('tmblr') != -1:
            continue
        if not util.checkRelated(link, list, keywords):
            continue
        links[link] = 'tweet'

    r = requests.get(searchUrl.format(token, phrase, link_limit))
    response = json.loads(r.content)
    if (response['status_code'] == 200):
        for result in response['data']['results']:
            link = result['aggregate_link']
            if not util.checkRelated(link, list, keywords):
                continue
            links[link] = 'bitly'
        return links
    else:
        print 'getNews/getLinks', response['status_code']
        sys.exit(1)

def getNewsInfo(links):
    print links
    news = []
    titles = []
    try:
        g = goose.Goose()
        for link in links:
            info = {}
            article = g.extract(url=link)
            title = article.title
            if not util.checkUnique(title, titles):
                continue
            titles.append(title)
            info['title'] = title
            info['link'] = link
            info['meta'] = article.meta_description[:150].encode('utf-8').strip()
            info['pic'] = None
            if article.top_image is not None:
                info['pic'] = article.top_image.src
            if info['pic'].find('.jpg') == -1 and info['pic'].find('.png') == -1:
                continue
            #info['category'] = getCategory(link)
            info['clicks'] = getClicks(link)
            info['link_ts'] = str(int(time.time()))
            info['text'] = None
            if article.cleaned_text is not None:
                info['text'] = article.cleaned_text[:150].encode('utf-8').strip() + '...'
            if info['text'] is None or info['text'] == '' or info['pic'] is None or info['pic'] == '':
                continue
            news.append(info)
        return news
    except:
        return news

        
def getCategory(link):
    all = ['Sports', 'Entertainment', 'Celebrity', 'Food', 'Technology', 'Politics', 'Business', 'News']
    r = requests.get(categoryUrl.format(token, link))
    response = json.loads(r.content)
    if (response['status_code'] == 200):
        list = response['data']['categories']
        result = ['News']
        for c in list:
            if c in all and c not in result:
                result.append(c)
        return ';'.join(result)
    else:
        print 'getNews/getInfo', response['status_code']
        sys.exit(1)

