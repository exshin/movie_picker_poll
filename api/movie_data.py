#!/usr/bin/python27

import requests
import json

def get_movie_info(movie, imdb_id=None):
	# get movie info using omdb api
	try:
		if imdb_id:
			omdb_api_string = 'http://www.omdbapi.com/?i='
			api_string = omdb_api_string + imdb_id + '&t='
		else:
			omdb_api_string = 'http://www.omdbapi.com/?i=&t='
			movie_string = movie.replace(' ','%20')
			api_string = omdb_api_string + movie_string
		r = requests.get(api_string)
		try:
			movie_info = r.json()
			test = movie_info.get('Title')
		except:
			movie_info = json.loads(r.content)
		test = movie_info.get('Title')
	except Exception as error:
		print error, "in get_movie_info"
		movie_info = None
	return movie_info
