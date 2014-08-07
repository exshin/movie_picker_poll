#!/usr/bin/python27

import os
import requests
from flask import Flask, make_response, render_template, request
from flask import send_from_directory, session, url_for, redirect
from datetime import datetime
from datetime import timedelta
from movie_picker import *

from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from authomatic.providers import oauth2

CONFIG = {
    'google': {
        'class_': oauth2.Google,
        'consumer_key': '634213859079-g48uqhs50ljkhjbuknrtobu9u68v6c37.apps.googleusercontent.com',
        'consumer_secret': 'd7994wiYgkWmY1M23hUU4CHf',
        'scope': oauth2.Google.user_info_scope + ['https://www.googleapis.com/auth/userinfo.profile',
                                                'https://www.googleapis.com/auth/userinfo.email'],
    },
}

app = Flask(__name__)
authomatic = Authomatic(CONFIG, 'A0Zr80j/3yX r~XHH!jmN]L^X/,?RT')

@app.route('/movie_poll', methods=['GET', 'POST'])
def login(provider_name='google'):
    response = make_response()
    # Authenticate the user
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    movie_results = get_movie_votes()
    if result:
        if result.user:
            # Get user info
            result.user.update()
            # Talk to Google API
            if result.user.credentials:
                response = result.provider.access('https://www.googleapis.com/oauth2/v1/userinfo?alt=json')
                if response.status == 200:
                    print response
            if result.user.email:
                print result.user.data
                session['user_name'] = result.user.data.get('displayName')
                session['user_email'] = result.user.email
        return render_template('movie_poll.html',
                            user=session['user_name'],
                            results=movie_results)
    return response

@app.route('/')
def index():
    return 'Nothing here'

@app.route('/results', methods=['GET','POST'])
def show_results():
    if request.method == 'POST':
        movie = request.form.get('movie')
        imdb_id = request.form.get('imdb_id')
        if imdb_id:
            print movie, '- ADD -', session.get('user_email')
            vote('', session.get('user_email'), imdb_id)
        else:
            print movie, '- VOTE -', session.get('user_email')
            vote(movie, session.get('user_email'))
    results = get_movie_votes()
    return render_template('results.html',results=results)

@app.route('/addnew', methods=['GET','POST'])
def add_new_movie():
    if request.method == 'POST':
        movie = request.form['addmovie']
        if movie:
            title_list = add_movie(movie)
    return render_template('addnew.html',title_list=title_list)

@app.route('/watched', methods=['GET','POST'])
def show_watched():
    # Get watched movies list
    watched_results = get_watched()
    return render_template('watched.html',results=watched_results)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')

@app.route('/clear_sessions')
def clear_sessions():
    session.clear()
    return """
        <p>Logged out</p>
        <p><a href="/movie_poll">Return to Movie Poll</a></p>
        """ 

app.secret_key = 'A0Zr80j/3yX r~XHH!jmN]L^X/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')