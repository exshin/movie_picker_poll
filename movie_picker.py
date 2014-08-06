#!/usr/bin/python27
#-*- coding: utf-8 -*-

from psycopg2 import connect
from db.queries import *
from configs.config import connStr
from api.movie_data import get_movie_info
from api.movie_posters import get_poster

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

def vote(movie, user_email=None):
	# write movie vote to database
	try:
		movie_info = get_movie_info(movie.lower())
		print movie_info.get('Plot')
		conn, dbCursor = connect_db()
		dbCursor.execute(sql_write_vote,[movie,user_email])
		conn.commit()
		if movie_info:
			movie_poster_url = get_poster(movie_info.get('imdbID'))
			dbCursor.execute(sql_insert_movie_data,[
				movie,
				movie_info.get('Title'),
				movie_info.get('Plot'),
				movie_info.get('Writer'),
				movie_info.get('Metascore'),
				movie_info.get('imdbRating'),
				movie_info.get('Director'),
				movie_info.get('Actors'),
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



