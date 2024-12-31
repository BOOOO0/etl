CREATE EXTERNAL TABLE IF NOT EXISTS movies_output (
  movie_id INT,
  title STRING,
  genre STRING,
  release_year INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar" = "\"",
  "escapeChar" = "\\"
)
LOCATION 's3://project-data-storage-cjdy7f/movies-output/'
TBLPROPERTIES ('skip.header.line.count'='1');


SELECT * 
FROM movies_output 
LIMIT 10;