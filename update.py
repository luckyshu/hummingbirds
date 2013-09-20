#!/usr/bin/env python

import getTrends
import getTweet
import getNews
import MySQLdb
import time
import sys
import util
import json
import os

cities = [['United States'], ['San Francisco', 'New York', 'Chicago'], ['Seattle', 'Washington', 'Houston'], ['Indianapolis', 'Boston', 'Miami'], ['Phoenix', 'Denver', 'Los Angeles']]


db = MySQLdb.connect("localhost","insight","1234","hummingbirds")
cursor = db.cursor()
city_group_id = int(sys.argv[1])
news_file = 'news_records'

trend_insert_query = """
    INSERT INTO trend 
    (last_updated, phrase, city)
    VALUES
    (%s, %s, %s)
    """
tweet_insert_query = """
    INSERT INTO tweet
    (created_at, trend_id, text, location, user, sentiment, url)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s)
    """
trend_update = """
    UPDATE trend
    SET positive_sentiment=%s, neutral_sentiment=%s, negative_sentiment=%s, keywords=%s
    WHERE id=%s
    """
news_insert_query = """
    INSERT INTO news
    (last_updated, clicks, url, title, meta, pic, text, source)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
    """
trend_news_insert_query = """
    INSERT INTO trend_news_junction
    (trend_id, trend_phrase, news_id)
    VALUES
    (%s, %s, %s)
    """
trend_exists_query = """
    select trend_id from trend_news_junction where trend_phrase = %s order by trend_id
    """

get_news_id_query = """
    select news_id from trend_news_junction where trend_id = %s
    """

for city in cities[city_group_id]:
    # GET TREND
    trends = getTrends.getTwitterTrends(city)
    ts = int(time.time())
    try:
	cursor.execute('update news set last_updated = %s where id = 191', (str(int(time.time()))))
        for trend in trends:
            print trend
            positive = 0
            neutral = 0
            negative = 0
            cursor.execute(trend_insert_query, (ts, trend, city))
            trend_id = db.insert_id()
            print trend_id

            #GET TWEETS
            tweet_list = getTweet.getTweets(city, trend)
            for tweet in tweet_list[1:]:
                cursor.execute(tweet_insert_query, (tweet['created_at'], trend_id, tweet['text'], tweet['location'], tweet['name'], tweet['sentiment'], tweet['url']))
                if tweet['sentiment'] > 0:
                    positive += 1
                if tweet['sentiment'] == 0:
                    neutral += 1
                if tweet['sentiment'] < 0:
                    negative += 1
        
            keywords = ';'.join(tweet_list[0].keys())
            
            if positive == 0 and neutral == 0 and negative == 0:
                positive_sentiment = None
                neutral_sentiment = None
                negative_sentiment = None
            else:
                positive_sentiment = float(positive) / len(tweet_list)
                neutral_sentiment = float(neutral) / len(tweet_list)
                #negative_sentiment = float(negative) / len(tweet_list)
                negative_sentiment = 1 - positive_sentiment - neutral_sentiment
            cursor.execute(trend_update, (positive_sentiment, neutral_sentiment, negative_sentiment, keywords, trend_id))

            #GET NEWS
            cursor.execute(trend_exists_query, (trend))
            rows = cursor.fetchall()
            if len(rows) >= 1:
                prev_trend_id = rows[0][0]
                cursor.execute(get_news_id_query, (prev_trend_id))
                rows = cursor.fetchall()
                for row in rows:
                    cursor.execute(trend_news_insert_query, (trend_id, trend, row[0]))
                
            else:
                links = getNews.getLinks(trend, tweet_list)
                new_links = []
                #IN ORDER TO REDUCE BITLY API CALLS, CHECK WHETHER THE LINK HAS BEEN STORED BEFORE
                cwd = os.path.dirname(os.path.abspath(__file__))
                records = {}
                news_records = os.path.join(cwd, news_file)
                if os.path.exists(news_records):
                    newsresults = open(news_records, 'r')
                    for line in newsresults:
                        fields = line.strip().split(',')
                        records[fields[0]] = fields[1]
                    newsresults.close()

                for link in links.keys():
                    if link in records.keys():
                        print 'link exists'
                        news_id = records[link]
                        cursor.execute(trend_news_insert_query, (trend_id, trend, news_id))
                    else:
                        new_links.append(link)
            
                newsresults = open(news_records, 'a')
                news_list = getNews.getNewsInfo(new_links)
                for news in news_list:
                    #print news['link_ts'], news['clicks'], news['link'], news['title'], news['meta'], news['pic'], news['text'], links[news['link']]
                    cursor.execute(news_insert_query, (news['link_ts'], news['clicks'], news['link'], news['title'], news['meta'], news['pic'], news['text'], links[news['link']]))
                    news_id = db.insert_id()
                    newsresults.write('%s,%s\n' % (news['link'], news_id))
                    cursor.execute(trend_news_insert_query, (trend_id, trend, news_id))
                newsresults.close()
             
            db.commit()

    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        db.rollback()
        sys.exit(1)

cursor.close()

