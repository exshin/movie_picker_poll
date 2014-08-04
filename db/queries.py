#!/usr/bin/python27
#-*- coding: utf-8 -*-


sql_movie_counts = """
SELECT DISTINCT
	v.movie
	,COUNT(v.id) count_votes
FROM
	votes v
	LEFT JOIN
	watched_movies w
	ON v.movie = w.movie
WHERE
	w.id IS NULL
GROUP BY
	v.movie
ORDER BY
	COUNT(v.id) desc
"""


sql_write_vote = """
INSERT INTO votes
(
	movie,
	vote_date
)
VALUES
(
	%s,
	current_date
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

