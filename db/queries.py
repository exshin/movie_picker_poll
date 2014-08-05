#!/usr/bin/python27
#-*- coding: utf-8 -*-


sql_movie_counts = """
SELECT DISTINCT
	v.movie
	,COUNT(DISTINCT v.user_email) count_votes
	,d.title
	,d.plot
	,d.imdbrating
	,d.rated
	,d.genre
	,d.movie_year
	,d.actors
	,d.poster
FROM
	votes v
	LEFT JOIN
	watched_movies w
	ON v.movie = w.movie
	LEFT JOIN
	movie_data d
	ON v.movie = d.movie
WHERE
	w.id IS NULL
GROUP BY
	v.movie
	,d.title
	,d.plot
	,d.imdbrating
	,d.rated
	,d.genre
	,d.movie_year
	,d.actors
	,d.poster
ORDER BY
	COUNT(DISTINCT v.user_email) desc
"""


sql_write_vote = """
INSERT INTO votes
(
	movie,
	vote_date,
	user_email
)
VALUES
(
	%s,
	current_date,
	%s
)
"""

sql_write_watched = """
INSERT INTO watched_movies
(
	movie,
	view_date
)
VALUES
(
	%s,
	current_date
)
"""

sql_get_watched = """
SELECT DISTINCT
	w.movie
	,w.view_date
	,to_char(w.view_date,'Mon')||' '||to_char(w.view_date,'dd')||' '||to_char(w.view_date,'YYYY') text_date
FROM
	watched_movies w
ORDER BY
	w.view_date desc
"""

sql_insert_movie_data = """
INSERT INTO movie_data
(  
  movie,
  title,
  plot,
  writer,
  metascore,
  imdbrating,
  director,
  actors,
  movie_year,
  genre,
  awards,
  runtime,
  poster,
  imdb_votes,
  imdbid,
  rated
)
VALUES
(
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s,
  %s
)
  """
