#!/usr/bin/python27
#-*- coding: utf-8 -*-

import requests
import json
from psycopg2 import connect
from db.queries import *
from configs.config import connStr

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
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_write_vote,[movie,user_email])
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

def get_movie_info(movie):
	# get movie info using omdb api
	omdb_api_string = 'http://www.omdbapi.com/?i=&t='
	r = requests.get(omdb_api_string+movie)
	movie_info = r.json()
	#TODO: structure data into a popup window that utilizes
	info_sample = {u'Plot': u"After discovering her boyfriend is married, Carly soon meets the wife he's been betraying. And when yet another love affair is discovered, all three women team up to plot revenge on the three-timing S.O.B.", u'Rated': u'PG-13', u'Response': u'True', u'Language': u'English', u'Title': u'The Other Woman', u'Country': u'USA', u'Writer': u'Melissa Stack', u'Metascore': u'39', u'imdbRating': u'6.2', u'Director': u'Nick Cassavetes', u'Released': u'25 Apr 2014', u'Actors': u'Cameron Diaz, Leslie Mann, Nikolaj Coster-Waldau, Don Johnson', u'Year': u'2014', u'Genre': u'Comedy, Romance', u'Awards': u'N/A', u'Runtime': u'109 min', u'Type': u'movie', u'Poster': u'http://ia.media-imdb.com/images/M/MV5BMTc0ODE4ODY1OF5BMl5BanBnXkFtZTgwMDA5NjkzMTE@._V1_SX300.jpg', u'imdbVotes': u'32,601', u'imdbID': u'tt2203939'}



