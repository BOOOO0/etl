from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, split

# SparkSession 생성
spark = SparkSession.builder \
    .appName("Movies ETL") \
    .getOrCreate()

# Extract: CSV 파일 읽기
movies_df = spark.read.csv("/Users/booyoung/Documents/Dev/etl/data/movies.csv", header=True, inferSchema=True)
ratings_df = spark.read.csv("/Users/booyoung/Documents/Dev/etl/data/ratings.csv", header=True, inferSchema=True)

# Transform: 평균 평점 계산
average_ratings_df = ratings_df.groupBy("movieId").agg(avg("rating").alias("average_rating"))

# 장르를 쉼표로 분리
movies_df = movies_df.withColumn("genres", split(col("genres"), "\\|"))

# 영화 데이터와 평균 평점 병합
result_df = movies_df.join(average_ratings_df, on="movieId", how="left")

# 결과를 콘솔에 출력 (5줄만)
result_df.show(5, truncate=False)

# Load: 결과 저장 (CSV로 저장)
# result_df.write.csv("transformed_movies", header=True, mode="overwrite")

print("ETL 작업이 완료되었습니다. 'transformed_movies' 디렉토리를 확인하세요.")
