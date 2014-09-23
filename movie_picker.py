#!/usr/bin/python27
#-*- coding: utf-8 -*-

from psycopg2 import connect
from db.queries import *
from configs.config import connStr
from api.movie_data import get_movie_info
from api.movie_posters import get_poster
from api.movie_titles import get_titles
from utils.util import utf_fix

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
		print error, ':: Get Results Unsuccessful'
		results = []
	return results

def my_movie_votes(user_email):
	# get movie votes within a given time frame
	try:
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_my_movie_counts,[user_email,])
		results = dbCursor.fetchall()
		conn.close()
	except Exception as error:
		print error, ':: Get Results Unsuccessful'
		results = []
	return results


def vote(movie, user_email=None, imdb_id=None):
	# write movie vote to database
	try:
		if imdb_id:
			movie_info = get_movie_info('',imdb_id=imdb_id)
		else:
			movie_info = get_movie_info(movie.lower())
		print movie_info.get('Title')
		print movie_info.get('Plot')
		conn, dbCursor = connect_db()
		dbCursor.execute(sql_write_vote,[utf_fix(movie_info.get('Title')),user_email])
		conn.commit()
		if movie_info:
			check_exist = dbCursor.execute(sql_check_movie_data,[movie_info.get('imdbID')])
			if not check_exist:
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
		print error, ':: Vote Unsuccessful'

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
		print error, ':: Add Watched Unsuccessful'

def get_watched():
	# Get list of watched movies
	try:
		conn,dbCursor = connect_db()
		dbCursor.execute(sql_get_watched)
		results = dbCursor.fetchall()
		conn.close()
	except Exception as error:
		print error, ':: Get Watched Unsuccessful'
		results = []
	return results


def vote_list_update(vote_list, user_email):
	# UPDATE movie votes per user
	try:
		if vote_list:
			conn, dbCursor = connect_db()
			dbCursor.execute(sql_delete_my_movies,[user_email])
			conn.commit()

			insert_list = []
			for imdbid in vote_list:
				insert_list.append([user_email,imdbid,'true'])
			args_str = ','.join(dbCursor.mogrify("(%s,%s,%s)", x) for x in insert_list)
			insert_query = sql_insert_my_movies + args_str
			dbCursor.execute(insert_query)
			conn.commit()

			conn.close()

			print 'Vote List Update Successful'
	except Exception as error:
		print error, ':: Vote List Update Unsuccessful'


def vote_single(imdb_id, user_email, vote_logic):
	# Update my_movies with single vote or unvote
	if imdb_id and user_email and vote_logic:
		conn, dbCursor = connect_db()
		try:
			if vote_logic == 'vote':
				print 'VOTE'
				dbCursor.execute(sql_insert_my_movies_single,[user_email,imdb_id,imdb_id,user_email])
			else:
				print 'REMOVE'
				dbCursor.execute(sql_delete_my_movies_single,[user_email,imdb_id])
			conn.commit()
			conn.close()
		except Exception as error:
			print error, "in vote_single, movie_picker.py", imdb_id, user_email, vote_logic
			conn.rollback()


def get_groups(user_email):
	# get list of groups
	conn, dbCursor = connect_db()
	dbCursor.execute(sql_get_groups,[user_email])
	group_list = dbCursor.fetchall()
	#group_list = [group_id,group_name,group_image,group_location,preview_movie,next_movie,member_count,is_user_a_member?]
	conn.close()
	return group_list

def insert_users(user_name,user_email,user_avatar,user_data,google_auth_id,admin_status='false'):
	# inserts users if they don't exist
	conn, dbCursor = connect_db()
	try:
		dbCursor.execute(sql_insert_new_users,
			[user_name,user_email,user_avatar,user_data,google_auth_id,admin_status,user_email])
		conn.commit()
		new_user_id = dbCursor.fetchall()
		conn.close()
	except Exception as error:
		print error, "--Error commiting new users"
		conn.rollback()
		new_user_id = None
	return new_user_id

def insert_groups(group_name,group_location,group_image,group_creator_id):
	# inserts new groups if the group name doesn't exist
	conn, dbCursor = connect_db()
	try:
		dbCursor.execute(sql_insert_new_groups,
			[group_name,group_location,group_image,group_creator_id,group_name])
		new_group_id = dbCursor.fetchall()
		if new_group_id:
			group_id = new_group_id[0]
			dbCursor.execute(sql_insert_new_group_members,
				[group_id,group_creator_id,'true',group_id,group_creator_id])
			first_group_member_id = dbCursor.fetchall()
			if first_group_member_id:
				print "Success! New group created: ",group_name
				conn.commit()
		else:
			group_id = None
		conn.close()
		return group_id
		
	except Exception as error:
		print error, "--Error commiting new group"
		conn.rollback()
		return None

def get_user_id(user_email):
	# get user_id
	conn, dbCursor = connect_db()
	try:
		dbCursor.execute(sql_get_user_id,[user_email])
		results = dbCursor.fetchall()
		if results:
			user_id = results[0]
		conn.close()
		return user_id
	except Exception as error:
		print error
		user_id = None
	return user_id


def join_leave_group(user_id,group_id,logic):
	# join or leave group
	conn, dbCursor = connect_db()
	if logic == 'join':
		try:
			dbCursor.execute(sql_insert_new_group_members,
					[group_id,user_id,'false',group_id,user_id])
			results = dbCursor.fetchall()
			if results:
				conn.commit()
				print 'User successfully joined - ', group_id
			conn.close()
		except Exception as error:
			print error, 'join logic error'
	else:
		try:
			dbCursor.execute(sql_delete_group_members,
					[user_id,group_id])
			conn.commit()
			print 'User successfully left - ', group_id
			conn.close()
		except Exception as error:
			print error, 'leave logic error'
