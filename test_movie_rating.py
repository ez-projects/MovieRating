#!/usr/bin/python3

from movie_rating import get_imdb_id_by_url
from movie_rating import get_movie_details_by_id
from movie_rating import get_movie_name_and_year
from movie_rating import create_query


def test_create_query():
    """
    """
    test_cases = [
        {
            "title": "The Lego Batman Movie",
            "year": "2017",
            "expected_query": "The Lego Batman Movie 2017"
        },
        {
            "title": "Assassin's Creed",
            "year": "2016",
            "expected_query": "Assassin's Creed 2016"
        },
        {
            "title": "Moonlight",
            "year": "2016",
            "expected_query": "Moonlight 2016"
        }
    ]
    for test in test_cases:
        actual_query = create_query(test["title"], test["year"])
        assert actual_query == test["expected_query"], \
            "Expected query: [{}], but got: [{}]".format(test["expected_query"], actual_query)

def test_get_imdb_id_by_url():
    """
    Test
    """
    movie_url = "http://www.imdb.com/title/tt6255746/?ref_=fn_ft_tt_1"
    expected_id = "tt6255746"
    actual_id = get_imdb_id_by_url(movie_url)
    assert expected_id == actual_id, "Expected movie id: [{}], but got: [{}]".format(expected_id, actual_id)

def test_get_movie_details_by_id():
    """
    Test get_movie_details_by_id()
    tt4116284
    """
    movie_id = "tt4116284"
    expected_movie_details = {
        "original_title": "The Lego Batman Movie",
        "title": "The Lego Batman Movie",
        "release_date": "2017-02-08",
        "vote_average": 7.2,
        "original_language": "en",
        "revenue": 310032902,
        "imdb_id": "tt4116284",
        "poster_path": "/snGwr2gag4Fcgx2OGmH9otl6ofW.jpg",
        "production_countries": [
            "Denmark",
            "United States of America"
        ]
    }
    actual_details = get_movie_details_by_id(movie_id)
    assert expected_movie_details == actual_details, \
        "Expected movie details: [{}], but got: [{}]".format(expected_movie_details, actual_details)

def test_get_movie_name_and_year():
    """
    :return:
    """
    filenames = [
        "Inner.Workings.2016.1080p.BluRay.x264-HDEX[EtHD]",
        "Moonlight.2016.720p.BluRay.x264-SPARKS[rarbg]",
        "The.Lego.Batman.Movie.2017.1080p.WEB-DL.DD5.1.H264-FGT",
        "Assassin's.Creed.2016.1080p.WEB-DL.DD5.1.H264-FGT"
    ]
    expected_results = [
        {
            "name": "Inner Workings",
            "year": "2016"
        },
        {
            "name": "Moonlight",
            "year": "2016"
        },
        {
            "name": "The Lego Batman Movie",
            "year": "2017"
        },
        {
            "name": "Assassin's Creed",
            "year": "2016"
        }
    ]
    for ind, name in enumerate(filenames):
        expected_name = expected_results[ind]["name"]
        expected_year = expected_results[ind]["year"]
        actual_name, actual_year = get_movie_name_and_year(name)
        assert expected_name == actual_name, \
            "Expected name: [{}], but got: [{}]".format(expected_name, actual_name)
        assert expected_year == actual_year, \
            "Expected year: [{}], but got: [{}]".format(expected_name, actual_year)
    # The same name should be returned
    irregular_name = "Some.Name.Without.Resolution.WEB-DL.DD5.1.H264-FGT"
    actual_name, actual_year = get_movie_name_and_year(irregular_name)
    expected_name = "Some Name Without Resolution Web-Dl Dd5 1"
    assert expected_name == actual_name, \
        "Expected name: [{}], but got: [{}]".format(expected_name, actual_name)
    assert not actual_year, "Expected year was None, but got: [{}]".format(actual_year)