from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, desc, year
from pyspark.sql.functions import split, explode
from pyspark.sql.functions import regexp_extract

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("Advanced ETL S3 to Redshift") \
    .getOrCreate()

# S3 경로 설정
ratings_path = "s3://my-etl-project-bucket/raw-data/ratings.csv"
movies_path = "s3://my-etl-project-bucket/raw-data/movies.csv"

# S3에서 데이터 읽기
ratings_df = spark.read.csv(ratings_path, header=True, inferSchema=True)
movies_df = spark.read.csv(movies_path, header=True, inferSchema=True)

# 데이터 정제: 결측치 제거 및 중복 제거
ratings_df = ratings_df.na.drop().dropDuplicates()
movies_df = movies_df.na.drop().dropDuplicates()

# 영화 연도 추출 (영화 제목에서 연도 추출)
movies_df = movies_df.withColumn("year", regexp_extract(col("title"), r"\((\d{4})\)", 1))
movies_df = movies_df.withColumn("year", col("year").cast("int"))

# 평점 데이터와 영화 데이터 결합
joined_df = ratings_df.join(movies_df, on="movieId")

# 장르별 평균 평점 계산
# 장르 컬럼을 분리하고 explode 사용해 여러 장르에 대해 처리
movies_genre_df = joined_df.withColumn("genres", explode(split(col("genres"), "\\|")))

genre_avg_rating = movies_genre_df.groupBy("genres") \
    .agg(avg("rating").alias("avg_rating"), count("rating").alias("rating_count")) \
    .orderBy(desc("avg_rating"))

# 연도별 상위 10 영화 추출 (평점 기준)
top_movies_by_year = joined_df.groupBy("year", "title") \
    .agg(avg("rating").alias("avg_rating"), count("rating").alias("rating_count")) \
    .filter("rating_count >= 50") \
    .orderBy("year", desc("avg_rating"))

# Top 10 영화 추천
top_10_movies = joined_df.groupBy("title") \
    .agg(avg("rating").alias("avg_rating"), count("rating").alias("rating_count")) \
    .filter("rating_count >= 100") \
    .orderBy(desc("avg_rating")) \
    .limit(10)

# 결과 저장
output_base_path = "s3://my-etl-project-bucket/transformed-data"

genre_avg_rating.write.mode("overwrite").parquet(f"{output_base_path}/genre_avg_rating")
top_movies_by_year.write.mode("overwrite").parquet(f"{output_base_path}/top_movies_by_year")
top_10_movies.write.mode("overwrite").parquet(f"{output_base_path}/top_10_movies")

# JSON 및 CSV 포맷으로 저장
genre_avg_rating.write.mode("overwrite").json(f"{output_base_path}/genre_avg_rating_json")
top_movies_by_year.write.mode("overwrite").csv(f"{output_base_path}/top_movies_by_year_csv")

print("Advanced ETL Job completed successfully!")
