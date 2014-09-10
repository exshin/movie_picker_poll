#!/usr/bin/python27
#-*- coding: utf-8 -*-


sql_movie_counts = """
SELECT DISTINCT
	d.movie
	,COUNT(DISTINCT my_votes.user_email) count_votes
	,d.title
	,d.plot
	,d.imdbrating
	,d.rated
	,d.genre
	,d.movie_year
	,d.actors
	,d.poster
	,d.imdbid
FROM
	movie_data d
	LEFT JOIN
	watched_movies w
	ON d.movie = w.movie
	LEFT JOIN
	my_movies my_votes
	ON my_votes.imdb_id = d.imdbid
WHERE
	w.id IS NULL
	AND
	d.title IS NOT NULL
	AND
	d.poster != ''
	
GROUP BY
	d.movie
	,d.title
	,d.plot
	,d.imdbrating
	,d.rated
	,d.genre
	,d.movie_year
	,d.actors
	,d.poster
	,d.imdbid
ORDER BY
	COUNT(DISTINCT my_votes.user_email) desc

"""

sql_my_movie_counts = """
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
	,d.imdbid
	,my_votes.my_vote
FROM
	votes v
	LEFT JOIN
	watched_movies w
	ON v.movie = w.movie
	LEFT JOIN
	movie_data d
	ON v.movie = d.movie
	LEFT JOIN
	my_movies my_votes
	ON my_votes.imdb_id = d.imdbid AND my_votes.user_email = %s
WHERE
	w.id IS NULL
	AND
	d.title IS NOT NULL
	AND
	d.poster != ''
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
	,d.imdbid
	,my_votes.my_vote
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
  rated,
  info_date
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
  %s,
  current_date
)
  """

sql_check_movie_data = """
SELECT DISTINCT imdbid FROM movie_data WHERE imdbid = %s
"""

sql_delete_my_movies = """
DELETE FROM my_movies WHERE user_email = %s;
"""

sql_insert_my_movies = """
INSERT INTO my_movies (user_email,imdb_id,my_vote)
VALUES """

#input [user_email,imdb_id,imdb_id,user_email]
sql_insert_my_movies_single = """
INSERT INTO my_movies (user_email,imdb_id,my_vote)
SELECT %s,%s,true
WHERE NOT EXISTS (SELECT id FROM my_movies WHERE imdb_id || user_email = %s||%s )
"""

sql_rated_stats = """
WITH mdata AS (
SELECT DISTINCT m.user_email, d.imdbid, d.movie, d.rated, d.genre, d.movie_year
FROM my_movies m LEFT JOIN movie_data d ON m.imdb_id = d.imdbid
ORDER BY m.user_email
)
SELECT DISTINCT
	m.rated category
	,SUM(CASE WHEN m.user_email = %s THEN 1 ELSE 0 END) user_total
	,(SUM(CASE WHEN imdbid IS NOT NULL THEN 1 ELSE 0 END) + 0.0)/ t.users avg
	,SUM(CASE WHEN imdbid IS NOT NULL THEN 1 ELSE 0 END) all_total
FROM
	mdata m
	LEFT JOIN
	(SELECT COUNT(DISTINCT user_email) users FROM mdata) t
	ON t.users IS NOT NULL
GROUP BY
	m.rated,t.users
ORDER BY
	m.rated asc
"""

sql_year_stats = """
WITH mdata AS (
SELECT DISTINCT m.user_email, d.imdbid, d.movie, d.rated, d.genre, d.movie_year
FROM my_movies m LEFT JOIN movie_data d ON m.imdb_id = d.imdbid
ORDER BY m.user_email
)
SELECT DISTINCT
	m.movie_year category
	,SUM(CASE WHEN m.user_email = %s THEN 1 ELSE 0 END) user_total
	,(SUM(CASE WHEN imdbid IS NOT NULL THEN 1 ELSE 0 END) + 0.0)/ t.users avg
	,SUM(CASE WHEN imdbid IS NOT NULL THEN 1 ELSE 0 END) all_total
FROM
	mdata m
	LEFT JOIN
	(SELECT COUNT(DISTINCT user_email) users FROM mdata) t
	ON t.users IS NOT NULL
GROUP BY
	m.movie_year,t.users
ORDER BY
	m.movie_year asc
"""

sql_imdbrating_stats = """
WITH mdata AS (
SELECT DISTINCT m.user_email, d.imdbid, d.movie
	,CASE WHEN d.imdbrating::numeric < 4 THEN '0-4' 
		WHEN d.imdbrating::numeric BETWEEN 4 AND 7 THEN '4-7' 
		WHEN d.imdbrating::numeric BETWEEN 7 AND 8 THEN '7-8'
		WHEN d.imdbrating::numeric BETWEEN 8 AND 9 THEN '8-9'
		ELSE '9-10' END imdbrating 
	, d.rated, d.genre, d.movie_year
FROM my_movies m LEFT JOIN movie_data d ON m.imdb_id = d.imdbid
ORDER BY m.user_email
)
SELECT DISTINCT
	m.imdbrating category
	,SUM(CASE WHEN m.user_email = %s THEN 1 ELSE 0 END) user_total
	,(SUM(CASE WHEN imdbid IS NOT NULL THEN 1 ELSE 0 END) + 0.0)/ t.users avg
	,SUM(CASE WHEN imdbid IS NOT NULL THEN 1 ELSE 0 END) all_total
FROM
	mdata m
	LEFT JOIN
	(SELECT COUNT(DISTINCT user_email) users FROM mdata) t
	ON t.users IS NOT NULL
GROUP BY
	m.imdbrating,t.users
ORDER BY
	m.imdbrating asc
"""


sql_genre_stats = """
SELECT DISTINCT m.user_email, d.imdbid, d.movie, d.rated, d.genre, d.movie_year
FROM my_movies m LEFT JOIN movie_data d ON m.imdb_id = d.imdbid
ORDER BY m.user_email
"""
