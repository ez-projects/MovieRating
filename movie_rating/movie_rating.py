#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json
from requests import get
from os import listdir
from os.path import isdir, join
import argparse

from bs4 import BeautifulSoup
from contextlib import closing
from json import dumps
from requests.exceptions import RequestException

MOVIE_ROOT = '/run/media/nathan/Seagate2Tb/HDerNew'
#'/run/media/nathan/Seagate4Tb/MOVIES/Movies'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('./log/movie_rating.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter(
    '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d [%(funcName)s]} \
    %(levelname)s - %(message)s','%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

BLACKLISTED_STR = ["(TV Movie)", ":", "(Short)"]
ALLOWED_CHAR = ["(I)", "(II)"]

def get_movies(folder_path):
    """
    Get a list of movies from the given folder
    """
    files = []
    print("\nTotal Movie: {}\n".format(len(listdir(folder_path))))
    try:
        for f in listdir(folder_path):
            if isdir(join(folder_path, f)):
                for ff in listdir(join(folder_path, f)):
                    if ff.endswith('.mkv'):
                        files.append(ff.replace('.mkv', ''))
            else:
                if f.endswith('.mkv'):
                    files.append(f.replace('.mkv', ''))
    except OSError as msg:
        logger.info("No movies were found in: {}".format(folder_path))
    logger.info("Get movies in directory: {}".format(folder_path))
    return files


def clean_up_string_between_year_and_resolution(movie_name):
    """
    movie_name:
        Wilson.2017.LIMITED.720p.BluRay.x264-GECKOS[rarbg]
        Labor.Day.2013.BluRay.1080p.DTS.x264-CHD.chs
        Daddys.Home.2.2017.1080p.WEB-DL.DD5.1.H264-FGT
    remove LIMITED, BluRay in the original movie name
    return: movie title and year in a list
    """
    title_and_year = []
    for item in movie_name.split("."):
        #import  ipdb; ipdb.set_trace()
        item = item.replace('(', '').replace(')', '')
        if item.isdigit() and len(item)==4:
            title_and_year.append(item)
            break
        else:
            title_and_year.append(item)

    year = f'{title_and_year[-1]}'
    series = title_and_year[-2]
    title = ''
    if series.isdigit():
        title = title_and_year[:-2]
    else:
        title = title_and_year[:-1]
        series = None

    # In the case there is no year info in the name
    if len(title_and_year) == len(movie_name.split(".")) and not \
        title_and_year[-1].isdigit():
        print("\nERROR: Invalid movie name: No year info was found\n")
        title_and_year = []

    return (' '.join(title), series, year)


def get_movie_name_and_year(name):
    """
    name: original folder name contains the movie
    return: movie name and year in a tuple
    """
    title_and_year = clean_up_string_between_year_and_resolution(name)
    # movie_name = ""
    # year = ""
    # if "720p" in name:
    #     movie_name = name.split("720p")[0].strip(".").replace(".", " ")
    # elif "1080p" in name:
    #     movie_name = name.split("1080p")[0].strip(".").replace(".", " ")
    # else:
    #     temp_title = ''
    #     for item in name.split('.'):
    #         try:
    #             parse(item, fuzzy=True).year
    #         except ValueError:
    #             temp_title += '{}.'.format(item)
    #         else:
    #             temp_title += '{}.'.format(item)
    #             break
    #     movie_name = temp_title.replace(".", " ").strip()

    # title = []
    # logger.info("File name: {}".format(name))
    # for x in movie_name.split(" ")[:-1]:
    #     if not set(x) & set(["(", ")", "'"]):
    #         title.append(x.title())
    #     else:
    #         title.append(x)
    # year = movie_name.split(" "[-1]
    # year = year if year.isdigit() else ""
    if title_and_year:
        year = title_and_year[-1]
        title = title_and_year[:-1]
        logger.info("Movie Title and Year: {} {}".format(title, year))
        return " ".join(title), year
    else:
        return "", ""


def create_query(movie_title, series, year):
    """
    movie_name: dotted notation name
    return query with name in + fashion
    """
    if not year.startswith('y:'):
        year = f'y:{year}'
    query = []
    # -1 is used to exclude year
    for i in movie_title.split(" "):
        if not set(["(", ")"]) & set(i):
            query.append(i)
    # add year separately
    if series:
        query.append(series)
    query.append(year)
    logger.info("Created query: {}".format(query))
    return " ".join(query)


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0}: {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (
        resp.status_code == 200
        and content_type is not None
        and content_type.find('html') > -1
    )


def log_error(e):
    """
    It is always a good idea to log errors
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_search_results(movie_title, series, year):
    """
    Get parsered html from search result
    :param movie_title:
    :param series:
    :param year:
    :return:
    """
    search_title = f'{movie_title} {series}' if series else f'{movie_title}'
    url = \
        f'http://www.imdb.com/search/title?title={search_title}&' + \
        f'title_type=feature&release_date={year}-01-01,{year}-12-31'
    logger.info("Get movie url from {}".format(url))
    logger.info("Searching for movie: {}".format(url))
    response = simple_get(url)
    html = BeautifulSoup(response, "html.parser")

    return html


def find_match_movie_from_search_result(html):
    """
    """
    result = html.find("h3", {"class": "lister-item-header"})
    # result = [i for i in result.find("div", {"class": "flex"}).children]
    # title =  result[1].get_text()
    # https://www.imdb.com/search/title?title=The+Hobbit+An+Unexpected+Journey&title_type=feature&release_date=2012-01-01,2012-12-31
    if not result:
        return None
    movie_href= result.find(href=True).get("href", None)

    movie_url = "http://www.imdb.com"
    # logger.info("Get movie url from {}".format(movie_url))
    # movie_href = ""
    # query = create_query(movie_title, series, year)
    #
    # url = 'https://www.themoviedb.org/search/movie?query="{}"'.format(query)
    # print(url)
    # logger.info("Searching for movie: {}".format(url))
    # expected_title = "{}".format(movie_title.lower())
    # expected_series = series
    # expected_year = "({})".format(year)
    # response = simple_get(url)
    # html = BeautifulSoup(response, "html.parser")
    # if html.find("div", {"class": "findNoResults"}):
    #     url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(query)
    #     response=simple_get(url)
    #     html = BeautifulSoup(response, "html.parser")
    #
    # table = html.find('table', {'class': 'findList'})
    # if table:
    #     rows = table.findAll('tr')
    #     found = False
    #     for tr in rows:
    #         cols = tr.findAll('td')
    #         for col in cols:
    #             col_text = \
    #                 str(col.text.encode('utf-8').decode('ascii', 'ignore').strip())
    #             if col_text:
    #                 for s in BLACKLISTED_STR:
    #                     col_text = col_text.replace(s, "").replace("'", '')
    #                 col_text = col_text.strip().lower()
    #                 # NB: identify movie in there
    #                 # if col_text.startswith(expected_title) and col_text.endswith(expected_year):
    #                 print(col_text)
    #                 if expected_series:
    #                     res = set(col_text.split(" ")) - \
    #                           set(
    #                               expected_title.split(" ") +
    #                               [expected_series] + [expected_year]
    #                           )
    #                 else:
    #                     res = set(col_text.split(" ")) - \
    #                           set(expected_title.split(" ") + [expected_year])
    #                 if (not res) or (res & set([x.lower() for x in ALLOWED_CHAR])):
    #                     movie_href = cols[1].find('a').get("href") or (not res in expected_title)
    #                     found = True
    #                     break
    #         if found:
    #             break
    movie_url += movie_href
    return movie_url


def get_imdb_id_by_url(url):
    """
    http://www.imdb.com/title/tt6255746/?ref_=fn_ft_tt_1
    """

    if url and url.split("/")[-2].startswith("tt"):
        logger.info("Get movie id from: {}".format(url))
        return url.split("/")[-2]
    else:
        return None


def get_movie_details_by_id(imdb_id):
    """
    https://api.themoviedb.org/3/movie/{imdb_id}?api_key=c73d7f19c33a3c43d4f4f66a80cde8d7
    original_title: string
    title: string
    release_date: string
    vote_average: number
    production_countries: list of dictionary
    original_language: string
    """
    url = "https://api.themoviedb.org/3/movie/{}?api_key=c73d7f19c33a3c43d4f4f66a80cde8d7&format=json".format(imdb_id)
    logger.info("Send GET request: {}".format(url))
    response = requests.get(url)
    # TODO: 1. create mongo query based on this information
    # TODO:      a. query {original_title: "", title: "", release_date: "", imdb_id:, id:""}
    # TODO: 2. Create Media DB with a collection called Movies
    # TODO: 3. Get poster: https://image.tmdb.org/t/p/w500/{poster_path}
    data = response.json()
    logger.info(dumps(data, indent=4))
    assert response.status_code == 200, "Expected response code: 200, but got {}".format(data, indent=4)
    refined_data = {
        "original_title": "",
        "title": "",
        "release_date": "",
        "vote_average": 0,
        "original_language": "",
        "revenue": 0,
        "imdb_id": "",
        "poster_path": ""
    }
    if data:
        production_countries = [country["name"] for country in data["production_countries"]]
        for key in refined_data.keys():
            refined_data[key] = data.get(key)
        refined_data["production_countries"] = production_countries
    logger.info(dumps(refined_data, indent=4))
    # pprint(refined_data)
    return data


def get_movie_rating_by_url(url, verify=False):
    """
    Get movie title to confirm
    Get movie rating
    """
    logger.info("Get movie rating from: {}".format(url))
    doc = simple_get(url)
    # doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    rating_div = soup.find('span', {"itemprop": 'ratingValue'})
    rating_str = str(rating_div)
    if verify:
        verify_searched_results(url, soup)
    # Get rating
    rating = rating_str.replace('</span>', "").split(">")[-1]
    logger.info("Movie Rating: {}".format(rating))
    return rating


def verify_searched_results(url, soup_html):
    """
    Verify movie title and year find on IMDB against themoviedb.org
    """
    print("Verifying... ...")
    imdb_id = get_imdb_id_by_url(url)
    verified_data = get_movie_details_by_id(imdb_id)
    title_div = soup_html.find("h1", {"itemprop":"name"}).get_text().encode('utf-8').decode('ascii', 'ignore')
    title_str = title_div.lower()
    # Verify movie title and year
    release_year = get_release_year_by_date(verified_data.get("release_date"))
    try:
        assert release_year in title_div, \
            "Expected to find [{}] in [{}].".format(release_year, str(title_div.encode('utf-8')))
        assert verified_data['title'].lower() in title_div.lower(), \
            "Expected to find [{}] in [{}].".format(verified_data['title'], str(title_div.encode('utf-8')))
    except AssertionError as msg:
        print("\tFailed: {}".format(msg))
    else:
        print("\tPASSED!!!")
    print(json.dumps(verified_data,indent=4))


def get_release_year_by_date(release_date):
    """
    release_date: 2016-05-14 accepted format
    """
    return release_date.split("-")[0]


def get_movie_poster_from_tmdb(poster_path, movie_path):
    """
    Get movie poster from https://image.tmdb.org and downlaod it to movie_path
    """
    if movie_path.endswith("/"):
         movie_path = movie_path[:-1]
    movie_folder_name = movie_path.split("/")[-1]
    poster_url = "https://image.tmdb.org/t/p/w500/{}".format(poster_path)
    logger.info("Get movie poster from: {}".format(poster_url))
    poster = "{}/{}.jpg".format(movie_path, movie_folder_name)
    # urllib.request.urlretrieve(poster_url, poster)
    logger.info("Movie poster was saved in: {}".format(poster))


def get_poster_url_by_imdb_id(imdb_id):
    """
    Get poster url from omdbapi
    http://omdbapi.com/?apikey=f6539eee&i=tt1507571&format=json
    :param imdb_id:
    :return: poster url
    """
    url =f'http://omdbapi.com/?apikey=f6539eee&i={imdb_id}&format=json'
    response = requests.get(url)
    response =json.loads(response.content)
    img_url = response.get("Poster", None)

    return img_url


def create_parsed_args():
    """
    --single: Find one given movie's rating
    --path: Find all movies' rating in the given path
    --poster: Find movie rating with poster path
    --preview: Find movie rating with preview link
    --verify: Verify the found movie's id at www.themoviedb.org
    """

    parser = argparse.ArgumentParser(
        prog='Movie Rating Finder',
        description='This simple web crawler find the given movies rating '\
            'from IMDB site. It will be used as part of the UI project.',
        usage='python movie_rating.py [OPTION] [VALUE]'
    )

    parser.add_argument('-s', '--single',
                        default=None,
                        help='To find a single given movie rating'
                       )
    parser.add_argument('-p', '--path',
                        default=MOVIE_ROOT,
                        help='To find all movies\'s rating in the given directory path'
                       )
    parser.add_argument('-v', '--verify',
                        default='True',
                        help='Verify movie\'s id from www.themoviedb.org'
                       )
    return parser.parse_args()


def parse_verify(verify_arg):
    """
    """
    if verify_arg.lower() in ['1', 'y', 'yes', 't', 'true']:
        return True
    else:
        return False


def main():
    """
    """
    parsed_args = create_parsed_args()
    movies = []
    verify = True if parse_verify(parsed_args.verify) else False
    # A movie name from command line
    if parsed_args.single:
        movies = [parsed_args.single]
    # A directory of movies
    else:
        path = parsed_args.path
        movies = get_movies(path)
        logger.info("Scanning movies in: {}".format(path))
    # Lookup movies
    for name in movies:
        print(name)
        movie_title, series, year = clean_up_string_between_year_and_resolution(name)
        # movie_title, series, year = get_movie_name_and_year(name)
        found_it = False
        movie_url = None
        imdb_id = None
        while not found_it:
            html_result = get_search_results(movie_title, series, year)
            if html_result:
                movie_url = find_match_movie_from_search_result(html_result)
                imdb_id = get_imdb_id_by_url(movie_url)
            if movie_url and imdb_id:
                found_it = True
                rating = get_movie_rating_by_url(movie_url, verify)
                print("{} ({}): {} / 10.0\n\n".format(movie_title, year, rating))
                # if verify_search_result():
                    # print(dumps(get_movie_details_by_id(imdb_id), indent=4))
            else:
                print(f"\nOriginal Movie: [{name}] wasn't found;\n")
                if input("Countinue search: yes/no\n") in ['yes', 'y']:
                    movie_title = input("Enter movie title:\n")
                    series = input("Enter series: \n")
                    year = input("Enter year of relase: \n")
                else:
                    found_it = True
                    continue
if __name__ == '__main__':
    main()
