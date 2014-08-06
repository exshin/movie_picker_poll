#!/usr/bin/python27

import requests
import json

def get_movie_info(movie):
	# get movie info using omdb api
	try:
		omdb_api_string = 'http://www.omdbapi.com/?i=&t='
		movie_string = movie.replace(' ','%20')
		r = requests.get(omdb_api_string+movie_string)
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
