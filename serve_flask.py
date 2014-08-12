#!/usr/bin/python27
#-*- coding: utf-8 -*-

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

app = Flask(__name__)
authomatic = Authomatic(CONFIG, 'A0Zr80j/3yX r~XHH!jmN]L^X/,?RT')

 CONFIG = {
'google': {
    'class_': oauth2.Google,
    'consumer_key': '634213859079-hv40hf2rh5ki00mhfa8tmejepon8g2h7.apps.googleusercontent.com',
    'consumer_secret': '5DpbsTa8CTpSbC4cen6u_7h5',
    'scope': oauth2.Google.user_info_scope + ['https://www.googleapis.com/auth/userinfo.profile',
                                            'https://www.googleapis.com/auth/userinfo.email'],
    },
}

@app.route('/')
def index():
    return 'Nothing here'

@app.route('/movies', methods=['GET', 'POST'])
def login_movies(provider_name='google'):

    response = make_response()
    # Authenticate the user
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
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
        my_movie_results = my_movie_votes(session['user_email'])
        return render_template('movies.html',
                            user=session['user_name'],
                            results=my_movie_results)
    return response

@app.route('/results', methods=['GET','POST'])
def show_results():
    if request.method == 'POST':
        movie = request.form.get('movie')
        imdb_id = request.form.get('imdb_id')
        vote_list = request.form.getlist('checkbox_movie')
        if imdb_id:
            print imdb_id, '- ADD -', session.get('user_email')
            vote('placeholder', session.get('user_email'), imdb_id)
        elif imdb_id:
            print movie, '- VOTE -', session.get('user_email')
            vote(movie, session.get('user_email'))
        else:
            print 'my_movies UPDATE VOTES ', session.get('user_email')
            print vote_list, len(vote_list)
            vote_list_update(vote_list,session.get('user_email'))
    results = get_movie_votes()
    return render_template('results.html',results=results,user=session['user_name'])


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
    return render_template('watched.html',results=watched_results,user=session['user_name'])

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