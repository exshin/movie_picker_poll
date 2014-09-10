#!/usr/bin/python27
#-*- coding: utf-8 -*-

import collections
import json
import csv
from psycopg2 import connect, extras
from db.queries import *
from configs.config import connStr
from utils.counter import Counter

def get_results_stats(user_email):
	# get results info
	try:
		bar_data = {}
		pie_data = {}
		conn = connect(connStr['heroku_movies'])
		dbCursor = conn.cursor(cursor_factory=extras.DictCursor)

		dbCursor.execute(sql_rated_stats,[user_email])
		rated = dbCursor.fetchall()
		dbCursor.execute(sql_year_stats,[user_email])
		years = dbCursor.fetchall()
		dbCursor.execute(sql_imdbrating_stats,[user_email])
		score = dbCursor.fetchall()
		dbCursor.execute(sql_genre_stats)
		genre_data = dbCursor.fetchall()
		user_total,avgs,genre_keys,genre_total = genre_calculate(genre_data,user_email)

		bar_data['rated'] = {
			'keys': [x.get('category') for x in rated],
			'user': [float(x.get('user_total')) for x in rated],
			'avg': [round(float(x.get('avg')),2) for x in rated]
		} 
		bar_data['years'] = {
			'keys': [x.get('category') for x in years],
			'user': [float(x.get('user_total')) for x in years],
			'avg': [round(float(x.get('avg')),2) for x in years]
		} 
		bar_data['rating'] = {
			'keys': [x.get('category') for x in score],
			'user': [float(x.get('user_total')) for x in score],
			'avg': [round(float(x.get('avg')),2) for x in score]
		} 
		bar_data['genre'] = {
			'keys': genre_keys,
			'user': user_total,
			'avg': avgs
		}

		genre_pie_data= []
		for n in range(0,len(genre_keys)):
			genre_pie_data.append([genre_keys[n],user_total[n],0,genre_total[n]])
		pie_data['rated'] = rated
		pie_data['years'] = years
		pie_data['rating'] = score
		pie_data['genre'] = genre_pie_data

	except Exception as error:
		print error, user_email, "Get Results Stats Error"

	return bar_data, pie_data

def calculate_frequencies(data):
	# calculate frequencies of given data set
	if data:
		freq = Counter(data)
		freq =  dict(freq)
		return freq
	else:
		return None

def genre_calculate(genre_data,user_email):
	# find avg and user sum for genre data
	genre, genre_user = '',''
	for row in genre_data:
		genre = genre + ', ' + row[4]
		if row[0] == user_email:
			genre_user = genre_user + ', ' + row[4]
	genre = genre.split(', ')[1:]
	genre_user = calculate_frequencies(genre_user.split(', ')[1:])
	genre_avg = calculate_frequencies(genre)
	genre_keys = list(set(genre))
	total_users = len(set([x.get('user_email') for x in genre_data]))
	user_total,avgs,genre_total = [],[],[]
	for key in genre_keys:
		genre_total.append(genre_avg.get(key)) #append genre total vote counts to list
		if key in genre_user.keys():
			user_total.append(genre_user.get(key)) #append user vote counts to list
		else:
			user_total.append(0)
		avgs.append(round(genre_avg.get(key)/(total_users+0.0),2)) #get averages
	return user_total,avgs,genre_keys,genre_total

def save_results_to_json(data):
	#save to json file
	with open('data/results_data.json', 'w') as outfile:
		json.dump(data, outfile)

def save_bar_results_to_csv(data):
	#save to multiple csv files for bar chart in static
	for key in data.keys():
		temp_list = [['Category', 'Your_Votes', 'Average_Votes']]
		for n in range(0,len(data[key].get('keys'))):
			temp_list.append([data[key].get('keys')[n],
							data[key].get('user')[n],
							data[key].get('avg')[n]])
		with open('static/data/'+key.title()+".csv", "wb") as f:
			writer = csv.writer(f)
			writer.writerows(temp_list)

def save_pie_results_to_csv(data):
	#save to multiple csv files for pie chart in static
	for key in data.keys():
		temp_list = [['Category','Type','Votes']]
		for n in range(0,len(data[key])):
			temp_list.append([data[key][n][0],
							'User',
							data[key][n][3]])
			temp_list.append([data[key][n][0],
							'Total',
							data[key][n][1]])
		with open('static/data/'+key.title()+"_pie.csv", "wb") as f:
			writer = csv.writer(f)
			writer.writerows(temp_list)
