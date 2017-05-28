# -*- coding: utf-8 -*-
#!/usr/bin/python
import re
from bs4 import BeautifulSoup
import requests
from pyquery import PyQuery as pq
import sys
from os import listdir
import os
from os.path import isfile, join, isdir


# name = 
name_list = [
    # "Fist.Fight.2017.720p.BluRay.x264-DRONES[rarbg]",
    # "The.Wizard.of.Lies.2017.1080p.WEBRip.DD5.1.x264-monkee",
    # "War.Machine.2017.1080p.NF.WEBRip.DD5.1.x264-SB",
    # "John.Wick.Chapter.2.2017.1080p.WEB-DL.DD5.1.H264-FGT",
    # "Colossal.2016.1080p.WEB-DL.AAC2.0.H264-FGT",
    # "The.Shack.2017.1080p.WEB-DL.DD5.1.H264-FGT",
    # "The.Lego.Batman.Movie.2017.1080p.WEB-DL.DD5.1.H264-FGT",
    # "The.Boss.Baby.2017.1080p.WEB-DL.DD5.1.H264-FGT",
    # "Logan.2017.1080p.WEB-DL.DD5.1.H264-FGT",
    # "Gifted.2017.1080p.HC.WEBRip.x264.AAC2.0-STUTTERSHIT",
    # "xXx.Return.of.Xander.Cage.2017.1080p.WEB-DL.DD5.1.H264-FGT",
    "War.Machine.2017.1080p.NF.WEBRip.DD5.1.x264-SB"
]

def get_movies(folder_path):
    """
    Get a list of movies from the given folder
    """
    # mypath = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in listdir(folder_path) if isdir(join(folder_path, f))]
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
    title = " ".join([x.title() for x in movie_name.split(" ")][:-1])
    # print(title)
    year = movie_name.split(" ")[-1]
    # print(year)
    return title, year

def create_query(movie_title, year):
    """
    movie_name: dotted notation name
    return query with name in + fashion
    """
    query = "{} {}".format(movie_title, year)
    return query 
    
def get_movie_url(movie_title, year):
    """
    """
    movie_url = "http://www.imdb.com"
    movie_href = ""
    query = create_query(movie_title, year)

    # print(query)
    url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt&ttype=ft&ref_=fn_ft".format(query)
    # print(url)
    expected_result = "{} ({})".format(movie_title, year)
    # print(expected_result)

    doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    if soup.find("div", {"class": "findNoResults"}):
        url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(query)
        # print("Search AGAIN: {}".format(url))
        doc=pq(url, method="get", verify=True)
        soup = BeautifulSoup(doc.html(), "html.parser")

    table = soup.find('table', {'class': 'findList'})
    rows = table.findAll('tr')
    found = False
    for tr in rows:
        cols = tr.findAll('td')
        for col in cols:
            col_text = str(col.text)
            col_text = col_text.replace(":", "")
            col_text_titled = []
            for s in col_text.split(" "):
                col_text_titled.append(s.title())
            # print("col_text: {}".format(" ".join(col_text_titled)))
            # print("expected_result: {}".format(expected_result))
            if expected_result in " ".join(col_text_titled):
                # print(col.text)
                # print(cols[1].find('a').get("href"))
                movie_href = cols[1].find('a').get("href")
                found = True
                break
        if found:
            break
    movie_url += movie_href
    # print(movie_url)
    return movie_url

def get_movie_rating(url):
    """
    """
    doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    # print(doc.html())
    rating_div = soup.find('span', {"itemprop": 'ratingValue'})
    # print(rating_div)
    rating_str = str(rating_div)
    # print(rating_str.replace('</span>', "").split(">")[-1])
    rating = rating_str.replace('</span>', "").split(">")[-1]
    return rating


path = "/run/media/nathan/DATA/Movies/"
movies = get_movies(path)
for name in movies:
    movie_title, year = get_movie_name_and_year(name)

    movie_url = get_movie_url(movie_title, year)

    rating = get_movie_rating(movie_url)

    print("{} ({}): {}\n\n".format(movie_title, year, rating))