import requests
import json
from datetime import datetime, timedelta
from secret import appkey, appsecret

# TODAY_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjJlMjBjMGQzLWM5ZDEtNGNlMC1iNWQwLWUxYjA0N2NhZWQwNSIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTczNTI3NDA4NiwiaWF0IjoxNzM1MTg3Njg2LCJqdGkiOiJQU1VJbnpVS2w2b3BOVGdwcWpiNnhYdjJpaWdGdTQxN3BEdUoifQ.8e5Gs7TNPGk1_jQquoJkh35idClylbVJxIBQfcWdc0IPAUBaeK2IHak4LVHLvmWgbZkdfu5BJOoVbRJUBtRufw"

def get_access_token():
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret,
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get access token: {response.status_code}")
        return None

def fetch_daily_data(symbol, access_token, start_date, end_date):
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
        "FID_COND_MRKT_DIV_CODE": "J",  # 주식 시장
        "FID_INPUT_ISCD": symbol,       # 종목 코드
        "FID_PERIOD_DIV_CODE": "D",    # 일봉
        "FID_ORG_ADJ_PRC": "0",        # 수정 주가 여부
        "FID_INPUT_DATE_1": start_date,  # 시작 날짜
        "FID_INPUT_DATE_2": end_date    # 종료 날짜
    }
    response = requests.get(url, headers=headers, params=params)

    # 요청 및 응답 상태 출력
    print("Request URL:", response.url)
    print("Request Headers:", headers)
    print("Request Params:", params)
    print("Response Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code == 200:
        return response.json().get("output", [])
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

if __name__ == "__main__":
    symbol = "005930"  # 삼성전자 종목 코드
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")  # 10일 전부터
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")    # 어제까지

    access_token = get_access_token()
    if access_token:
        print(f"Access Token: {access_token}")
        daily_data = fetch_daily_data(symbol, access_token, start_date, end_date)
        if daily_data:
            print("✅ 가져온 데이터:")
            for entry in daily_data[:5]:  # 상위 5개 데이터만 출력
                print(entry)
        else:
            print("❌ 데이터를 가져오지 못했습니다.")
