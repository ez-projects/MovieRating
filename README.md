# MovieRating
[![Build
Status](https://travis-ci.org/zhou-en/MovieRating.svg?branch=master)](https://travis-ci.org/zhou-en/MovieRating)

Find the movie rating from IMDB

### Get movie rating by file name
```
python movie_rating/movie_rating.py -s [movie_file_name]
```

### Run Tests

```bash
pytest -v ./tests/test_movie_rating.py
```

### Tmuxinator Configure File
`Tmuxinator` installation instruction: https://github.com/tmuxinator/tmuxinator
There is a tmuxinator configure file **movie_rating.tmuxinator.yml** for
managing `tmux` windows and panes. This file needs to be copied or linked to
`~/.config/tmuxinator/` and started with `tmuxinator start
movie_rating.tmuxinator`.
