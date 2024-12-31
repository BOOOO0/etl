LOAD DATA LOCAL INFILE '/home/hadoop/data/movies.csv'
INTO TABLE movies
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS (userId, movieId, rating, timestamp);


LOAD DATA LOCAL INFILE '/home/hadoop/data/ratings.csv'
INTO TABLE ratings
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS (userId, movieId, rating, timestamp);
