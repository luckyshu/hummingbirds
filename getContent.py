#!/usr/bin/env python

import MySQLdb
import time
import sys
import json

db = MySQLdb.connect("localhost","insight","1234","hummingbirds")
d = []
cursor = db.cursor()
s = """select id, title, text, clicks, url, pic, last_updated from news join (select distinct news_trend.newsid as maxid from (select news.id as newsid, clicks, trend_news_junction.trend_id as trendid from news join trend_news_junction on news.id = trend_news_junction.news_id) as news_trend join (select trend_news_junction.trend_id as trendid2, max(clicks) as maxclicks from news join trend_news_junction on news.id = trend_news_junction.news_id where clicks > 30 group by trend_news_junction.trend_id) as max_clicks on news_trend.trendid = max_clicks.trendid2 and news_trend.clicks = max_clicks.maxclicks) as max on news.id = max.maxid order by last_updated desc limit 20;"""
cursor.execute(s)
rows = cursor.fetchall()
id = 1
for row in rows:
    news = {}
    news['id'] = "collapse" + str(id)
    news['title'] = unicode(row[1], errors='ignore')
    news['text'] = unicode(row[2], errors='ignore')
    news['clicks'] = row[3]
    news['url'] = row[4]
    news['pic'] = row[5]
    timestamp = int(row[6])
    news['last_updated'] = time.strftime('%b %d %Y %H:%M:%S', time.localtime(timestamp))
    trends = []
    cities = []
    related = []
    positive_sentiment = 0.0
    negative_sentiment = 0.0
    neutral_sentiment = 0.0
    s = 'select distinct trend_phrase from trend_news_junction where news_id = %s group by trend_phrase'
    cursor.execute(s, (row[0]))
    phrase_rows = cursor.fetchall()
    for phrase_row in phrase_rows:
        phrase = phrase_row[0]
        trends.append(phrase)
    trend = phrase_rows[0][0]
    s = 'select distinct city, positive_sentiment, negative_sentiment, neutral_sentiment from trend where phrase = %s group by city'
    cursor.execute(s, (trend))
    city_rows = cursor.fetchall()
    for city_row in city_rows:
        if city_row[0] != 'United States':
            cities.append(city_row[0])
	    if city_row[1] is None: 
		positive_sentiment += 0
	    else:
                positive_sentiment += city_row[1]
	    if city_row[2] is None:
		negative_sentiment += 0
	    else:
		negative_sentiment += city_row[2]
	    if city_row[3] is None:
		neutral_sentiment += 0
	    else:
                neutral_sentiment += city_row[3]
    news['positive'] = round(positive_sentiment / float(len(city_rows)), 2)
    news['neutral'] = round(neutral_sentiment / float(len(city_rows)), 2)
    news['negative'] = 1 - news['positive'] - news['neutral']

    news['trends'] = ', '.join(trends)
    news['city'] = ', '.join(cities)
        
    s = 'select id, title, text, clicks, url, pic, last_updated from news join (select distinct news_id as id2 from trend_news_junction where trend_id in (select trend_id from trend_news_junction where news_id = %s) and news_id != %s) as related on news.id = related.id2 where clicks > 30 and clicks < %s order by clicks desc limit 5'
    cursor.execute(s, (row[0], row[0], row[3]))
    related_rows = cursor.fetchall()
    sub_id = 1
    for related_row in related_rows:
        related_new = {}
        related_new['id'] = "collapse" + str(id) + str(sub_id)
        related_new['title'] = unicode(related_row[1], errors='ignore')
        related_new['text'] = unicode(related_row[2], errors='ignore')
        related_new['clicks'] = related_row[3]
        related_new['url'] = related_row[4]
        related_new['pic'] = related_row[5]
        timestamp = int(row[6])
        related_new['last_updated'] = time.strftime('%b %d %Y %H:%M:%S', time.localtime(timestamp))
        related.append(related_new)
        sub_id += 1
    news['related'] = related
    d.append(news)
    id += 1 
content = open('/home/ubuntu/hummingbirds/app/static/content.data', 'w')
with content as outfile:
    json.dump(d, outfile)
    outfile.write('\n')
content.close()
