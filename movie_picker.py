#!/usr/bin/python27
#-*- coding: utf-8 -*-

from psycopg2 import connect
from db.queries import sql_movie_counts, sql_write_vote
from configs.config import connStr

def connect_db(connection='heroku_movies'):
	# connect to database
	try:
		conn = connect(connStr[connection])
		dbCursor = conn.cursor()
	except Exception as error:
		print error
		dbCursor = None
	return dbCursor

def get_movie_votes(date_start,date_end):
	# get movie votes within a given time frame
	try:
		dbCursor = connect_db()
		dbCursor.execute(sql_movie_counts,[date_start,date_end])
		results = dbCursor.fetchall()
	except Exception as error:
		print error, 'Get Results Unsuccessful'
		results = []
	return results

def vote(movie):
	# write movie vote to database
	try:
		dbCursor = connect_db()
		dbCursor.execute(sql_write_vote,[movie,])
	except Exception as error:
		print error, 'Vote Unsuccessful'
