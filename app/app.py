from flask import Flask, session, flash, request, g
from flask import redirect, url_for, render_template
import MySQLdb
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    d = []
    cursor = g.db.cursor()
    s = """select id, title, text, clicks, url, pic, last_updated from news join (select distinct news_trend.newsid as maxid from (select news.id as newsid, clicks, trend_news_junction.trend_id as trendid from news join trend_news_junction on news.id = trend_news_junction.news_id) as news_trend join (select trend_news_junction.trend_id as trendid2, max(clicks) as maxclicks from news join trend_news_junction on news.id = trend_news_junction.news_id where clicks > 30 group by trend_news_junction.trend_id) as max_clicks on news_trend.trendid = max_clicks.trendid2 and news_trend.clicks = max_clicks.maxclicks) as max on news.id = max.maxid order by last_updated desc limit 20;
    """
    cursor.execute(s)
    rows = cursor.fetchall()
    print rows
    id = 1
    for row in rows:
        news = {}
        news['id'] = "collapse" + str(id)
        news['title'] = row[1]
        news['text'] = row[2]
        news['clicks'] = row[3]
        news['url'] = row[4]
        news['pic'] = row[5]
        timestamp = int(row[6])
        news['last_updated'] = time.strftime('%d %b %Y %H:%M:%S', time.localtime(timestamp))
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
                positive_sentiment += city_row[1]
                negative_sentiment += city_row[2]
                neutral_sentiment += city_row[3]
        news['positive'] = round(positive_sentiment / float(len(city_rows)), 2)
        #news['negative'] = round(negative_sentiment / float(len(city_rows)), 2)
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
            related_new['title'] = related_row[1]
            related_new['text'] = related_row[2]
            related_new['clicks'] = related_row[3]
            related_new['url'] = related_row[4]
            related_new['pic'] = related_row[5]
            timestamp = int(row[6])
            related_new['last_updated'] = time.strftime('%d %b %Y %H:%M:%S', time.localtime(timestamp))
            related.append(related_new)
            sub_id += 1
        news['related'] = related
        d.append(news)
        id += 1 
    #print d
    return render_template('news.html', d = d)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/slideshare')
def slideshare():
    return render_template('slideshare.html')

@app.before_request
def db_connect():
    g.db = MySQLdb.connect("localhost","insight","1234","hummingbirds")

@app.teardown_request
def db_disconnect(exception=None):
    g.db.close()
    
if __name__ == "__main__":
    app.run(debug = True)
