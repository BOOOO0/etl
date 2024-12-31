from pyspark.sql import SparkSession

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("MySQL RDS to S3") \
    .config("spark.driver.extraClassPath", "/usr/share/aws/emr/jdbc-drivers/mysql-connector-j-8.0.33.jar") \
    .getOrCreate()

# MySQL RDS 연결 정보
mysql_url = "jdbc:mysql://example-mysql-db-instance.cfk88uaw2pv9.ap-northeast-2.rds.amazonaws.com:3306/moviedb"
mysql_properties = {
    "user": "admin",
    "password": "your_password",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# RDS에서 데이터 읽기
movies_df = spark.read.jdbc(url=mysql_url, table="movies", properties=mysql_properties)

print("Data successfully loaded from MySQL.")

# S3 경로
s3_output_path = "s3://project-data-storage-cjdy7f/movies-output"

# S3에 데이터 저장
movies_df.write.csv(s3_output_path, mode="overwrite", header=True)

print(f"Data successfully written to S3 at {s3_output_path}!")
