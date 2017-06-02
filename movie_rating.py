# -*- coding: utf-8 -*-
#!/usr/bin/python
import re, pprint
import pudb
from bson.json_util import dumps
from bs4 import BeautifulSoup
import requests
from pyquery import PyQuery as pq
import sys
from os import listdir
import os
from os.path import isfile, join, isdir

def get_movies(folder_path):
    """
    Get a list of movies from the given folder
    """
    # mypath = os.path.dirname(os.path.realpath(__file__))
    files = []
    try:
        files = [f for f in listdir(folder_path) if isdir(join(folder_path, f))]
    except OSError as msg:
        print("No movies were found in: {}".format(folder_path))
    return files

def get_movie_name_and_year(name):
    """
    name: original folder name contains the movie
    return: movie name with year in dotted notation
    """
    movie_name = ""
    year = ""
    if "720p" in name:
        movie_name = name.split("720p")[0].strip(".").replace(".", " ")
        # print(movie_name)
    elif "1080p" in name:
        movie_name = name.split("1080p")[0].strip(".").replace(".", " ")
    else: 
        movie_name = name
    title = []
    for x in movie_name.split(" ")[:-1]:
        if not set(x) & set(["(", ")"]):
            title.append(x.title())
        else:
            title.append(x)
    # print(title)
    year = movie_name.split(" ")[-1]
    # print(year)
    
    return " ".join(title), year

def create_query(movie_title, year):
    """
    movie_name: dotted notation name
    return query with name in + fashion
    """
    query = []
    # -1 is used to exclude year
    for i in movie_title.split(" "):
        if not set(["(", ")"]) & set(i):
            query.append(i)
    # add year separately
    query.append(year)
    return " ".join(query)
    
def get_movie_url(movie_title, year):
    """
    """
    movie_url = "http://www.imdb.com"
    movie_href = ""
    query = create_query(movie_title, year)

    url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt&ttype=ft&ref_=fn_ft".format(query)
    expected_result = "{} ({})".format(movie_title, year)
    expected_result = expected_result.lower()
    doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    if soup.find("div", {"class": "findNoResults"}):
        url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(query)
        doc=pq(url, method="get", verify=True)
        soup = BeautifulSoup(doc.html(), "html.parser")
    table = soup.find('table', {'class': 'findList'})
    rows = table.findAll('tr')
    found = False
    for tr in rows:
        cols = tr.findAll('td')
        pudb.set_trace()
        for col in cols:
            col_text = str(col.text.strip())
            col_text = col_text.replace(":", "").replace("(TV Movie)", "").strip()
            if expected_result == col_text.lower():
                movie_href = cols[1].find('a').get("href")
                found = True
                break
        if found:
            break
    movie_url += movie_href
    return movie_url

def get_movie_rating(url):
    """
    """
    doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    rating_div = soup.find('span', {"itemprop": 'ratingValue'})
    rating_str = str(rating_div)
    rating = rating_str.replace('</span>', "").split(">")[-1]
    return rating

def main():
    movies = []
    # A movie name from command line
    if len(sys.argv) == 2:
        movies = [sys.argv[-1]]
    # A directory of movies
    else:
        path = "/run/media/nathan/DATA/Moviess/"
        movies = get_movies(path)
    # No movies were found/given, use these movies for testing
    if not movies:
        movies = [
            # "Arrival.(II).2016.1080p.WEB-DL.DD5.1.H264-FGT",
            # "The.Boss.Baby.2017.1080p.WEB-DL.DD5.1.H264-FGT",
            # "Logan.2017.1080p.WEB-DL.DD5.1.H264-FGT",
            # "Gifted.2017.1080p.HC.WEBRip.x264.AAC2.0-STUTTERSHIT",
            # "War.Machine.2017.1080p.NF.WEBRip.DD5.1.x264-SB",
            # "Colossal.2016.1080p.WEB-DL.AAC2.0.H264-FGT.mkv",
            "Gold.2016.1080p.WEB-DL.DD5.1.H264-FGT",
            "The.Wizard.of.Lies.2017.1080p.WEBRip.DD5.1.x264-monkee",
            "Jackie.2016.1080p.WEB-DL.DD5.1.H264-FGT",
            "Manchester.by.the.Sea.2016.1080p.WEB-DL.DD5.1.H264-FGT",
            # "Zai.Jian,.Zai.Ye.Bu.Jian.2016.720p.BluRay.x264-WiKi",
            # "Moonlight.(I).2016.720p.BluRay.x264-SPARKS[rarbg]",
            "The.Lego.Batman.Movie.2017.1080p.WEB-DL.DD5.1.H264-FGT"
        ]
        print("Using testing movie list: \n")
        print(dumps(movies, indent=4))
    
    # Lookup movies
    for name in movies:
        movie_title, year = get_movie_name_and_year(name)

        movie_url = get_movie_url(movie_title, year)

        rating = get_movie_rating(movie_url)
        print(name)
        print("{} ({}): {} / 10.0\n\n".format(movie_title, year, rating))

if __name__ == '__main__':
    main()