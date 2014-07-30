#!/usr/bin/python27

from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime
from movie_picker import *

app = Flask(__name__)

@app.route('/')
def show_poll():
    today = datetime.today().date()
    start_date = (datetime.today()-timedelta(days=7)).date()
    results = get_movie_votes(start_date,today)
    return render_template('movie_poll.html',results=results)

@app.route('/', methods=['GET','POST'])
def new_vote():
    movie = request.form['radio_movie']
    if not movie:
        movie = request.form['other_movie']
    vote(movie)
    results = get_movie_votes(start_date,today)
    return render_template('results.html',results=results)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')