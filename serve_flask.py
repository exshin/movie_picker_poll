#!/usr/bin/python27
#-*- coding: utf-8 -*-

import os
import requests
from flask import Flask, make_response, render_template, request, jsonify
from flask import send_from_directory, session, url_for, redirect
from datetime import datetime
from datetime import timedelta
from movie_picker import *
from results_stats import get_results_stats, save_bar_results_to_csv, save_pie_results_to_csv
import json

from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from authomatic.providers import oauth2

CONFIG = { 'google': {
        'class_': oauth2.Google,
        'consumer_key': '634213859079-mgc49r52otjltocu8hflks93tagflis0.apps.googleusercontent.com',
        'consumer_secret': 'xnGxvrPy0DUdsoF-z9KTi_ur',
        'scope': oauth2.Google.user_info_scope + ['https://www.googleapis.com/auth/userinfo.profile',
                                                'https://www.googleapis.com/auth/userinfo.email'],
        },
    }

app = Flask(__name__)
authomatic = Authomatic(CONFIG, 'A0Zr80j/3yX r~XHH!jmN]L^X/,?RT')

@app.route('/')
def index():
    return redirect("/movies", code=302)

@app.route('/movies', methods=['GET', 'POST'])
def login_movies(provider_name='google'):
    response = make_response()
    if not session.get('user') or not session.get('user_email'):
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
                    session['user'] = session['user_name'].split(' ')[0]
                    session['user_email'] = result.user.email
                    session['user_data'] = result.user.data
                    if result.user.data.get('image'):
                        session['profile_image_url'] = result.user.data['image'].get('url')
                    else:
                        session['profile_image_url'] = "http://www.neurosynaptic.com/wp-content/uploads/2014/05/avatar-blank.jpg"
                    insert_users(session['user_name'],session['user_email'],session['profile_image_url'],json.dumps(session['user_data']),session['user_data'].get('id'))
            my_movie_results = my_movie_votes(session['user_email'])
            my_votes = []
            for row in my_movie_results:
                if row[11]:
                    my_votes.append(row[10])
            return render_template('movies.html',
                user=session['user'],
                user_pic=session['profile_image_url'],
                results=my_movie_results,
                my_votes=my_votes)
    else:
        my_movie_results = my_movie_votes(session['user_email'])
        my_votes = []
        insert_users(session['user_name'],session['user_email'],session['profile_image_url'],json.dumps(session['user_data']),session['user_data'].get('id'))
        for row in my_movie_results:
            if row[11]:
                my_votes.append(row[10])
        return render_template('movies.html',
                user=session['user'],
                user_pic=session['profile_image_url'],
                results=my_movie_results,
                my_votes=my_votes)
    return response

@app.route('/results', methods=['GET','POST'])
def show_results():
    if request.method == 'POST':
        movie = request.form.get('movie')
        imdb_id = request.form.get('imdb_id')
        imdb_id_add = request.form.get('imdb_id_add')
        vote_list = request.form.getlist('checkbox_movie')
        if imdb_id_add:
            print imdb_id_add, '- ADD -', session.get('user_email')
            vote('placeholder', session.get('user_email'), imdb_id_add)
        elif movie:
            print movie, '- VOTE -', session.get('user_email')
            vote(movie, session.get('user_email'))
        else:
            print 'my_movies UPDATE VOTES ', session.get('user_email')
            print vote_list, len(vote_list)
            vote_list_update(vote_list,session.get('user_email'))
    results = get_movie_votes()
    return render_template('results.html',
                            results=results,
                            user=session['user'],
                            user_pic=session['profile_image_url'])

@app.route('/addnew', methods=['GET','POST'])
def add_new_movie():
    if request.method == 'POST':
        movie = request.form['addmovie']
        if movie:
            title_list = add_movie(movie)
    return render_template('addnew.html',title_list=title_list)


@app.route('/watched')
def show_watched():
    # Get watched movies list
    if session.get('user') and session.get('user_email'):
        watched_results = get_watched()
        return render_template('watched.html',
                            results=watched_results,
                            user=session['user'],
                            user_pic=session['profile_image_url'])
    else:
        return redirect("/movies", code=302)

@app.route('/stats', methods=['GET','POST'])
def show_results_stats():
    if session.get('user') and session.get('user_email'):
        bar_data, pie_data = get_results_stats(session['user_email'])
        save_bar_results_to_csv(bar_data)
        #save_pie_results_to_csv(pie_data) //not ready yet
        return render_template('results_stats.html',
                                user=session['user'],
                                user_pic=session['profile_image_url'])
    else:
        return redirect("/movies", code=302)

@app.route('/voteclick/', methods=['GET'])
def voteclick():
    # TESTING new features/ UI
    ret_data = {"value": request.args.get('vote_imdbID')}
    imdbID = str(request.args.get('vote_imdbID'))
    logic = str(request.args.get('vote_logic'))
    print session['user_email'], logic.title(), imdbID
    # insert or remove depending on logic
    vote_single(imdbID, session['user_email'], logic)
    # query new my_votes
    my_movie_results = my_movie_votes(session['user_email'])
    my_votes = []
    for row in my_movie_results:
        if row[11]:
            my_votes.append(row[10])
    print my_votes
    return jsonify({'votes': my_votes})


@app.route('/profile')
def profilepage():
    # Display profile page
    return """
        <p>Profile Page (Work in Progress) </p>
        <p><a href="/movies">Return to Home</a></p>
        """ 


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

@app.route('/logout')
def logout():
    session.clear()
    return """
        <p>Logged out</p>
        <p><a href="/movies">Return to Home</a></p>
        """ 

app.secret_key = 'A0Zr80j/3yX r~XHH!jmN]L^X/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=80)