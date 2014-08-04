#!/usr/bin/python27
#-*- coding: utf-8 -*-


sql_movie_counts = """
SELECT DISTINCT
	v.movie
	,COUNT(DISTINCT v.user_email) count_votes
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

