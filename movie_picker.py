#!/usr/bin/python27
#-*- coding: utf-8 -*-

from psycopg2 import connect
from db.queries import *
from configs.config import connStr
from api.movie_data import get_movie_info
from api.movie_posters import get_poster
from api.movie_titles import get_titles
from utils.util import uft_fix

def connect_db(connection='heroku_movies'):
	# connect to database
	try:
		conn = connect(connStr[connection])
		dbCursor = conn.cursor()
	except Exception as error:
		print error
		dbCursor = None
		conn = None
	return conn,dbCursor

def get_movie_votes():
	# get movie votes within a given time frame
	try:
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_movie_counts)
		results = dbCursor.fetchall()
		conn.close()
	except Exception as error:
		print error, 'Get Results Unsuccessful'
		results = []
	return results

def vote(movie, user_email=None, imdb_id=None):
	# write movie vote to database
	try:
		if imdb_id:
			movie_info = get_movie_info('',imdb_id=imdb_id)
		else:
			movie_info = get_movie_info(movie.lower())
		print movie_info.get('Plot')
		conn, dbCursor = connect_db()
		dbCursor.execute(sql_write_vote,[utf_fix(movie_info.get('Title')),user_email])
		conn.commit()
		if movie_info:
			movie_poster_url = get_poster(movie_info.get('imdbID'))
			dbCursor.execute(sql_insert_movie_data,[
				utf_fix(movie_info.get('Title')),
				utf_fix(movie_info.get('Title')),
				utf_fix(movie_info.get('Plot')),
				utf_fix(movie_info.get('Writer')),
				movie_info.get('Metascore'),
				movie_info.get('imdbRating'),
				utf_fix(movie_info.get('Director')),
				utf_fix(movie_info.get('Actors')),
				movie_info.get('Year'),
				movie_info.get('Genre'),
				movie_info.get('Awards'),
				movie_info.get('Runtime'),
				movie_poster_url,
				movie_info.get('imdbVotes'),
				movie_info.get('imdbID'),
				movie_info.get('Rated')
				])
			conn.commit()
		conn.close()
	except Exception as error:
		print error, 'Vote Unsuccessful'

def add_movie(movie,limit=5):
	# get a list of movies and summary for user to select the correct one
	add_movie_list = []
	titles = get_titles(movie,limit=limit)
	for row in titles:
		movie_info = get_movie_info(row[0],row[1])
		movie_poster_url = get_poster(row[1])
		add_movie_list.append([row[0] #movie title
							,row[1] #imdb_id
							,movie_poster_url
							,movie_info.get('Actors')
							,movie_info.get('Director')
							,movie_info.get('Genre')
							,movie_info.get('Plot')
							,movie_info.get('imdbRating')
							,movie_info.get('Title')
							])
	return add_movie_list 

def watched(movie):
	# Add viewed movies to the database
	try:
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_write_watched,[movie,])
		conn.commit()
		conn.close()
	except Exception as error:
		print error, 'Add Watched Unsuccessful'

def get_watched():
	# Get list of watched movies
	try:
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_get_watched)
		results = dbCursor.fetchall()
		conn.close()
	except Exception as error:
		print error, 'Get Watched Unsuccessful'
		results = []
	return results



