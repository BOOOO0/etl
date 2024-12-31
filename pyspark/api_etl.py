from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import requests
import os
import sys
from datetime import datetime, timedelta

# Spark 세션 초기화
spark = SparkSession.builder \
    .appName("FetchDailyStockData") \
    .getOrCreate()

# 명령줄 인자에서 날짜 가져오기
def get_target_date():
    target_date = None
    for arg in sys.argv:
        if arg.startswith("--date="):
            target_date = arg.split("=")[1]  # "--date=YYYYMMDD"에서 날짜 부분 추출
    if not target_date:
        raise ValueError("Target date not provided. Use --date=YYYYMMDD")
    return target_date

# 함수: 일별 데이터 가져오기
def fetch_daily_data(symbol, token, target_date):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "tr_id": "FHKST03010100",  # 주식 일봉 조회용 TR_ID
        "custtype": "P",
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": symbol,
        "FID_PERIOD_DIV_CODE": "D",
        "FID_ORG_ADJ_PRC": "0",
        "FID_INPUT_DATE_1": target_date,
        "FID_INPUT_DATE_2": target_date
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("output", [])
    else:
        print(f"Failed to fetch data for {symbol}: {response.status_code}")
        return []

# Main: 데이터 호출 및 S3 저장
if __name__ == "__main__":
    # 명령줄에서 날짜 가져오기
    target_date = get_target_date()

    # 환경 변수에서 토큰 가져오기
    TODAY_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijc1MmE2NzY4LTYzMzYtNDg1MS1iYTZiLWRkOWYxY2VlN2JhNCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTczNTYwMzUzNywiaWF0IjoxNzM1NTE3MTM3LCJqdGkiOiJQU1VJbnpVS2w2b3BOVGdwcWpiNnhYdjJpaWdGdTQxN3BEdUoifQ.hNghf__h6qUN9PXOhYM7P0EwmgoX4lxrf5MhBPMOqurvdttOgqT_CUgophFSldAC9rr73SS8hnFZuFbAFoMnmA"

    bucket_name = "project-data-storage-zhtkuo"  # S3 버킷 이름

    # 주식 코드 설정
    symbols = [("035420", "NAVER"), ("035720", "KAKAO"), ("005930", "SAMSUNG")]

    # 각 종목의 데이터 호출 및 Spark 데이터프레임 생성
    all_data = []
    for symbol, company_name in symbols:
        data = fetch_daily_data(symbol, TODAY_TOKEN, target_date)
        if data:
            for entry in data:
                entry["symbol"] = symbol
                entry["company_name"] = company_name
            all_data.extend(data)

    # Spark 데이터프레임 변환
    if all_data:
        df = spark.createDataFrame(all_data)

        # 컬럼 추가 및 데이터 정리
        df = df.withColumn("ingestion_time", lit(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # RDBMS에 적합한 형태로 데이터 구조화
        df = df.select(
            "company_name",
            "symbol",
            "stck_bsop_date",  # 거래 날짜
            "stck_clpr",       # 종가
            "stck_oprc",       # 시가
            "stck_hgpr",       # 고가
            "stck_lwpr",       # 저가
            "acc_trdvol",      # 거래량
            "ingestion_time"
        )

        # S3에 저장
        output_path = f"s3://{bucket_name}/daily_stock_data/"
        df.write.mode("append").parquet(output_path)  # append 모드로 저장

        print(f"✅ 데이터가 S3에 추가 저장되었습니다: {output_path}")
    else:
        print("❌ 데이터를 가져오지 못했습니다.")
