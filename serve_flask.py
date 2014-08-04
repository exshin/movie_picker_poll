#!/usr/bin/python27

import os
from flask import Flask, make_response, render_template, request
from flask import send_from_directory
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
authomatic = Authomatic(CONFIG, 'random secret string for session signing')

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
                    pass
        return render_template('movie_poll.html',
                            user=result.user,
                            results=movie_results)
    return response

@app.route('/')
def index():
    return 'Nothing here'

@app.route('/results', methods=['GET','POST'])
def show_results():
    if request.method == 'POST':
        movie = request.form['movie']
        if movie:
            print movie
            vote(movie)
    results = get_movie_votes()
    return render_template('results.html',results=results)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')