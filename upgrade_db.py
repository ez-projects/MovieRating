#!/venv/bin/python
# -*- coding: utf-8 -*-
"""
1. Go through /run/media/nathan/Seagate4Tb/MOVIES/, create a file of movie
names in the current test directory
2. Go through the movie list:
    if it's not in the database (query the original name):
        update database
    if it's in the database
        update database only if imdb rating is different
"""

from settings import MOVIE_ROOT