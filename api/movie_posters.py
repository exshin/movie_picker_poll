#!/usr/bin/python27

import requests
import json

def size_str_to_int(x):
    return float("inf") if x == 'original' else int(x[1:])

def get_poster(imdb_id):
	try:
		CONFIG_PATTERN = 'http://api.themoviedb.org/3/configuration?api_key={key}'
		KEY = '36bf44860d9a57841949fa74711ccf27'
		 
		url = CONFIG_PATTERN.format(key=KEY)
		r = requests.get(url)
		try:
			config = r.json()
		except:
			config = r.json

		base_url = config['images']['base_url']
		sizes = config['images']['poster_sizes']
		"""
		    'sizes' should be sorted in ascending order, so
		        max_size = sizes[-1]
		    should get the largest size as well.        
		"""

		max_size = max(sizes, key=size_str_to_int)

		IMG_PATTERN = 'http://api.themoviedb.org/3/movie/{imdbid}/images?api_key={key}' 
		r = requests.get(IMG_PATTERN.format(key=KEY,imdbid=imdb_id))
		try:
			api_response = r.json()
		except:
			api_response = r.json

		posters = api_response['posters']
		poster_urls = []
		for poster in posters:
		    rel_path = poster['file_path']
		    url = "{0}{1}{2}".format(base_url, max_size, rel_path)
		    poster_urls.append(url)

		"""
		for nr, url in enumerate(poster_urls):
		    r = requests.get(url)
		    filetype = r.headers['content-type'].split('/')[-1]
		    filename = 'poster_{0}.{1}'.format(nr+1,filetype) 
		    with open(filename,'wb') as w:
		        w.write(r.content)

		"""
		return poster_urls[0]

	except Exception as error:
		return 'http://media.gadgetsin.com/2014/04/the_superhero_minimalist_poster_collection_2.jpg'
