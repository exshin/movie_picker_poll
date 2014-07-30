#!/usr/bin/python27
#-*- coding: utf-8 -*-


sql_movie_counts = """
SELECT DISTINCT
	v.movie
	,COUNT(v.id) count_votes
FROM
	votes v
WHERE
	v.vote_date BETWEEN %s AND %s
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

