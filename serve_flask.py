#!/usr/bin/python27

from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime
from datetime import timedelta
from movie_picker import *

app = Flask(__name__)

@app.route('/')
def index():
    return 'Nothing here'


@app.route('/movie_poll', methods=['GET','POST'])
def show_poll():
    today = datetime.today().date()
    start_date = (datetime.today()-timedelta(days=7)).date()
    results = get_movie_votes(start_date,today)
    print results
    movie = request.form['other_movie']
    print movie
    vote(movie)
    return render_template('movie_poll.html',results=results)

@app.route('/results')
def show_results():
    today = datetime.today().date()
    start_date = (datetime.today()-timedelta(days=7)).date()
    results = get_movie_votes(start_date,today)
    return render_template('results.html',results=results)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')