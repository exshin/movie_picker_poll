#!/usr/bin/python27

import imdb

def get_titles(movie, limit=10):
	# get a list of possible titles and imdb ids
	movie = movie.lower()
	ia = imdb.IMDb()
	results = ia.search_movie(movie)
	title_list = []
	for row in results[:limit]:
		title_list.append([row['long imdb canonical title'],'tt'+str(row.movieID)])
	return title_list



