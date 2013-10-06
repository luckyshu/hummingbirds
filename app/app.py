from flask import Flask, session, flash, request, g
from flask import redirect, url_for, render_template
import MySQLdb
import time
import sys
import os
import json

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

#@app.route('/')
#@app.route('/index')
#def index():
    #return render_template('index.html')

@app.route('/')
@app.route('/news')
def news():
    content_path = os.path.join(os.path.curdir, 'content.data')
    d = []
    if os.path.exists(content_path):
        content = open(content_path, 'r')
        for line in content:
            d = json.loads(line)
        content.close()
    else:
        content = open('content.data.bak', 'r')
        for line in content:
            d = json.loads(line)
        content.close()
    return render_template('news.html', d = d)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/slides')
def slides():
    return render_template('slides.html')
'''
@app.before_request
def db_connect():
    #g.db = MySQLdb.connect("localhost","insight","1234","hummingbirds")

@app.teardown_request
def db_disconnect(exception=None):
    #g.db.close()
    '''
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True)

