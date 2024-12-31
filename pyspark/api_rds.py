from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import requests
from datetime import datetime, timedelta
from secret import appkey, appsecret
import json

# Spark 세션 초기화
spark = SparkSession.builder \
    .appName("FetchDailyStockData") \
    .getOrCreate()

# MySQL 접속 정보
mysql_host = "example-mysql-db-instance.cfk88uaw2pv9.ap-northeast-2.rds.amazonaws.com"
mysql_user = "admin"
mysql_password = "your_password"
mysql_db = "stock"  # 데이터베이스 이름
mysql_table = "stock_daily_data"  # 테이블 이름

# 함수: 일별 데이터 가져오기
def fetch_daily_data(symbol, company_name, access_token):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {access_token}",
        "appKey": appkey,
        "appSecret": appsecret,
        "tr_id": "FHKST03010100",
        "custtype": "P",
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": symbol,
        "FID_PERIOD_DIV_CODE": "D",
        "FID_ORG_ADJ_PRC": "0",
        "FID_INPUT_DATE_1": (datetime.now() - timedelta(days=365)).strftime("%Y%m%d"),
        "FID_INPUT_DATE_2": datetime.now().strftime("%Y%m%d"),
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        response_data = response.json()
        if "output2" in response_data and response_data["output2"]:
            for entry in response_data["output2"]:
                entry["symbol"] = symbol
                entry["company_name"] = company_name
            return response_data["output2"]
        else:
            print(f"No data in output2 for symbol {symbol}")
            return []
    else:
        print(f"Failed to fetch data for {symbol}: {response.status_code}")
        return []

# Main: 데이터 호출 및 MySQL 저장
if __name__ == "__main__":
    # 동적으로 인증 토큰 가져오기
    access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijc1MmE2NzY4LTYzMzYtNDg1MS1iYTZiLWRkOWYxY2VlN2JhNCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTczNTYwMzUzNywiaWF0IjoxNzM1NTE3MTM3LCJqdGkiOiJQU1VJbnpVS2w2b3BOVGdwcWpiNnhYdjJpaWdGdTQxN3BEdUoifQ.hNghf__h6qUN9PXOhYM7P0EwmgoX4lxrf5MhBPMOqurvdttOgqT_CUgophFSldAC9rr73SS8hnFZuFbAFoMnmA"

    symbols = [("035420", "NAVER"), ("035720", "KAKAO"), ("005930", "SAMSUNG")]

    all_data = []
    for symbol, company_name in symbols:
        data = fetch_daily_data(symbol, company_name, access_token)
        all_data.extend(data)

    if all_data:
        df = spark.createDataFrame(all_data)

        # 컬럼 정리: ingestion_time 제거
        df = df.select(
            "company_name",
            "symbol",
            "stck_bsop_date",  # 거래 날짜
            "stck_clpr",       # 종가
            "stck_oprc",       # 시가
            "stck_hgpr",       # 고가
            "stck_lwpr",       # 저가
            "acml_vol"         # 누적 거래량
        )

        # MySQL에 데이터 저장
        jdbc_url = f"jdbc:mysql://{mysql_host}:3306/{mysql_db}"
        df.write.format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", mysql_table) \
            .option("user", mysql_user) \
            .option("password", mysql_password) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()

        print(f"✅ 데이터가 MySQL 데이터베이스에 저장되었습니다: {mysql_table}")
    else:
        print("❌ 데이터를 가져오지 못했습니다.")