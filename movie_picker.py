#!/usr/bin/python27
#-*- coding: utf-8 -*-

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

def vote(movie):
	# write movie vote to database
	try:
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_write_vote,[movie,])
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
		print error, 'Vote Unsuccessful'


#TODO Google Auth Login
#TODO One movie per person 
