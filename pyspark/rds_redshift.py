from pyspark.sql import SparkSession

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("MySQL RDS to Redshift") \
    .config("spark.driver.extraClassPath", "/usr/share/aws/emr/jdbc-drivers/mysql-connector-j-8.0.33.jar:/usr/share/aws/emr/jdbc-drivers/redshift-jdbc42-2.1.0.30.jar") \
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

# Redshift JDBC URL (계정 정보 포함)
redshift_url = "jdbc:redshift://data-engineering-redshift.cpwost4fgucr.ap-northeast-2.redshift.amazonaws.com:5439/analytics?user=admin&password=Password1234"

# 데이터를 Redshift에 저장
movies_df.write \
    .format("jdbc") \
    .option("url", redshift_url) \
    .option("dbtable", "movies") \
    .option("driver", "com.amazon.redshift.jdbc42.Driver") \
    .mode("overwrite") \
    .save()

print("Data successfully written to Redshift!")
