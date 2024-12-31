resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "aws_s3_bucket" "project_bucket" {
  bucket = "project-data-storage-${random_string.suffix.result}"

  tags = {
    Environment = "Production"
    Project     = "ETL_Project"
  }
}

# resource "aws_s3_object" "movies_csv" {
#   bucket = aws_s3_bucket.project_bucket.id
#   key    = "data/movies.csv" # S3 버킷 내 파일 경로
#   source = "../data/movies.csv" # 로컬 파일 경로
# }

# resource "aws_s3_object" "ratings_csv" {
#   bucket = aws_s3_bucket.project_bucket.bucket
#   key    = "data/ratings.csv" # S3 버킷 내 파일 경로
#   source = "../data/ratings.csv" # 로컬 파일 경로
# }

# resource "aws_s3_object" "simple_pyspark" {
#   bucket = aws_s3_bucket.project_bucket.bucket
#   key    = "pyspark/simple.py" # S3 버킷 내 파일 경로
#   source = "../pyspark/simple.py" # 로컬 파일 경로
# }