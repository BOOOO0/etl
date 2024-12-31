from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import requests
import os
import sys
from datetime import datetime, timedelta
from secret import appkey, appsecret  # secret에서 appkey와 appsecret 가져오기
import json

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
        # 명령줄에서 날짜를 제공하지 않을 경우 오늘 날짜 사용
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")  # 기본값: 어제 날짜
        print(f"명령줄 인자에서 날짜를 제공하지 않았습니다. 기본값({target_date})을 사용합니다.")
    return target_date


# 함수: 일별 데이터 가져오기
def fetch_daily_data(symbol, access_token, target_date):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {access_token}",
        "appKey": appkey,
        "appSecret": appsecret,
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
    
    # 디버깅용 출력
    print("Request URL:", response.url)
    print("Request Headers:", headers)
    print("Request Params:", params)
    print("Response Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code == 200:
        # JSON 파싱
        response_data = response.json()
        if "output1" in response_data:  # output1의 데이터 반환
            return [response_data["output1"]]
        else:
            print(f"No data in output1 for symbol {symbol}")
            return []

# Main: 데이터 호출 및 S3 저장
if __name__ == "__main__":
    # 명령줄에서 날짜 가져오기
    target_date = get_target_date()

    # 동적으로 인증 토큰 가져오기
    access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijc1MmE2NzY4LTYzMzYtNDg1MS1iYTZiLWRkOWYxY2VlN2JhNCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTczNTYwMzUzNywiaWF0IjoxNzM1NTE3MTM3LCJqdGkiOiJQU1VJbnpVS2w2b3BOVGdwcWpiNnhYdjJpaWdGdTQxN3BEdUoifQ.hNghf__h6qUN9PXOhYM7P0EwmgoX4lxrf5MhBPMOqurvdttOgqT_CUgophFSldAC9rr73SS8hnFZuFbAFoMnmA"

    # 주식 코드 설정
    symbols = [("035420", "NAVER"), ("035720", "KAKAO"), ("005930", "SAMSUNG")]

    # 각 종목의 데이터 호출 및 Spark 데이터프레임 생성
    all_data = []
    for symbol, company_name in symbols:
        data = fetch_daily_data(symbol, access_token, target_date)
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
            "stck_prdy_clpr",  # 종가
            "stck_oprc",       # 시가
            "stck_hgpr",       # 고가
            "stck_lwpr",       # 저가
            "acml_vol",        # 누적 거래량
            "ingestion_time"   # 적재 시간
        )

       # DataFrame 출력
        df.show(truncate=False)  # 전체 데이터 출력
    else:
        print("❌ 데이터를 가져오지 못했습니다.")