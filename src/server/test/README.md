## Load Test Data

### Create Test Table

```
CREATE TABLE mldb.movie (
	_id serial PRIMARY KEY,
	series_title text,
	released_year varchar(100),
	certificate varchar(100),
	runtime varchar(100),
	genre text,
	imdb_rating float8,
	overview text,
	meta_score int4,
	director varchar(100),
	star1 varchar(100),
	star2 varchar(100),
	star3 varchar(100),
	star4 varchar(100),
	no_of_votes int4,
	gross varchar(100)
);
```

### Upload Data to table

- Use tools to import file resource/movie.csv

### Test Commands

```
python3 -m unittest test.sqlparser
python3 -m unittest test.select_query
python3 -m unittest test.predict_query
```
