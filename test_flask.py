#!/usr/bin/python27
#-*- coding: utf-8 -*-

import os
import requests
import json
from flask import Flask, make_response, render_template, request, jsonify
from flask import send_from_directory, session, url_for, redirect
from datetime import datetime
from datetime import timedelta
from movie_picker import *
from results_stats import get_results_stats, save_bar_results_to_csv, save_pie_results_to_csv

from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from authomatic.providers import oauth2

CONFIG = {
    'google': {
        'class_': oauth2.Google,
        'consumer_key': '634213859079-o7rqvrbdjee2l7g1nh78mra0c2ge0avj.apps.googleusercontent.com',
        'consumer_secret': 'AY28GUQNZ5puGNbAOy3V4Jhf',
        'scope': oauth2.Google.user_info_scope + ['https://www.googleapis.com/auth/userinfo.profile',
                                                'https://www.googleapis.com/auth/userinfo.email'],
    },
}

app = Flask(__name__)
authomatic = Authomatic(CONFIG, 'A0Zr80j/3yX r~XHH!jmN]L^X/,?RT')

@app.route('/movies', methods=['GET', 'POST'])
def login_movies(provider_name='google'):
    response = make_response()
    if not session.get('user') or not session.get('user_email') or not session.get('user_data'):
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
                    new_user_id = insert_users(session['user_name'],session['user_email'],session['profile_image_url'],json.dumps(session['user_data']),session['user_data'].get('id'))
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

@app.route('/test', methods=['GET'])
def test_html():
    # TESTING new features/ UI
    session['user_name'] = 'Eugene Chinveeraphan'
    session['user_email'] = 'chinveeraphan@gmail.com'
    session['profile_image_url'] = 'https://lh5.googleusercontent.com/-gLFJEhiapWU/AAAAAAAAAAI/AAAAAAAAAlA/m3J840QcgKc/photo.jpg?sz=50'
    session['user'] = session['user_name'].split(' ')[0]
    my_movie_results = my_movie_votes(session['user_email'])
    my_votes = []
    for row in my_movie_results:
        if row[11]:
            my_votes.append(row[10])
    return render_template('test.html',
                user=session['user'],
                user_pic=session['profile_image_url'],
                results=my_movie_results,
                my_votes=my_votes)

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

@app.route('/groupjoinleave/',methods=['GET'])
def groupjoinleave():
    return_data = {"value": request.args.get('group_id')}
    group_id = str(request.args.get('group_id'))
    logic = str(request.args.get('group_join_or_leave'))
    print session['user_email'], logic.title(), group_id
    # insert or remove from user_groups list
    user_id = get_user_id(session.get('user_email'))
    if user_id:
        join_leave_group(user_id,group_id,logic)
    # query new groups list
    # create ID list
    groups_list = get_groups(session.get('user_email'))
    groups_id_list = []
    for row in groups_list:
        if row[0] and row[8] == 1:
            groups_id_list.append(row[0])
    return jsonify({'groups_id': groups_id_list})

@app.route('/hide_poster/',methods=['GET'])
def hide_poster():
    return_data = {"value": request.args.get('hide_imdbid')}
    imdbid = str(request.args.get('hide_imdbid'))
    logic = 'remove'
    print session['user_email'], logic.title(), imdbid
    # add removed ids to hide_movies table
    hide_movies(session.get('user_email'),imdbid,logic)
    return jsonify({'hide_imdbid': imdbid})


@app.route('/profile')
def profilepage():
    # Display profile page
    return """
        <p>Profile Page (Work in Progress) </p>
        <p><a href="/movies">Return to Home</a></p>
        """ 

@app.route('/')
def index():
    return redirect("/movies", code=302)
    
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

@app.route('/events')
def show_events_landing():
    # Get watched movies list
    if session.get('user') and session.get('user_email'):
        return render_template('events.html')
    else:
        return redirect("/movies", code=302)

@app.route('/groups',methods=['GET','POST'])
def show_groups():
    # Get groups list
    if session.get('user_email'):
        if request.method == 'POST':
            group_name = request.form.get('group_name')
            group_location = request.form.get('group_location')
            group_image = request.form.get('group_image')
            if group_name and group_location and group_image:
                user_id = get_user_id(session.get('user_email'))
                new_group_id = insert_groups(group_name,group_location,group_image,user_id)
        groups_list = get_groups(session.get('user_email'))
        groups_id_list = []
        for row in groups_list:
            if row[0] and row[8] == 1:
                groups_id_list.append(row[0])
        return render_template('groups.html',
                            groups_list=groups_list,
                            groups_id_list=groups_id_list,
                            user=session['user'],
                            user_pic=session['profile_image_url'])
    else:
        return redirect("/movies", code=302)

@app.route('/stats', methods=['GET','POST'])
def show_results_stats():
    session['user_email'] = 'chinveeraphan@gmail.com'
    session['user_name'] = 'Eugene Chinveeraphan'
    session['user'] = session['user_name'].split(' ')[0]
    bar_data, pie_data = get_results_stats(session['user_email'])
    save_bar_results_to_csv(bar_data)
    #save_pie_results_to_csv(pie_data)
    return render_template('results_stats.html',
                                user=session['user'],
                                user_pic=session['profile_image_url'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico')


@app.route('/clear_sessions')
def clear_sessions():
    session.clear()
    return """
        <p>Logged out</p>
        <p><a href="/movies">Return to Movie Poll</a></p>
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
    url_for('data', filename='results_data.json')