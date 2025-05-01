import requests
from dotenv import load_dotenv
from datetime import datetime
import os

today = datetime.today()
formatted_date = today.strftime("%Y.%m.%d")

# 1. .env 파일 로드
load_dotenv()

# 2. 환경변수 사용
OPINET_API_KEY = os.getenv("OPINET_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# 오늘 기준
def get_gas_today_price():
    url = f"http://www.opinet.co.kr/api/avgSigunPrice.do?out=json&sido=11&sigun=1101&code={OPINET_API_KEY}" # 11: 제주도, 1101: 제주시
    
    try:
        r = requests.get(url)
        data = r.json()

        if "RESULT" not in data:
            return "오피넷 API 응답 에러가 발생했습니다."

        price_list = data["RESULT"]["OIL"]

        message = f"*⛽ 오늘({formatted_date})의 제주시 휘발유/경유 평균 가격*\n"
        for item in price_list:
            if item['PRODCD'] == 'B027':
               message += f"• 휘발유: {item['PRICE']}원\n"
               message += f"• 전일 대비: {item['DIFF']} {'⬆️' if item['DIFF'] > 0 else '⬇️'}\n\n"
            if item['PRODCD'] == 'D047':
                message += f"• 경유: {item['PRICE']}원\n"
                message += f"• 전일 대비: {item['DIFF']} {'⬆️' if item['DIFF'] > 0 else '⬇️'}"
            
        print(f"{message}")
        return message
    except Exception as e:
        return f"데이터 가져오기 실패: {e}"

# 제주시 휘발유 최저가 Top10 주유소
def get_gas_min_price():
    url = f"http://www.opinet.co.kr/api/lowTop10.do?out=json&code={OPINET_API_KEY}&prodcd=B027&area=1101&cnt=10" # 11: 제주도, 1101: 제주시
    
    try:
        r = requests.get(url)
        data = r.json()

        if "RESULT" not in data:
            return "오피넷 API 응답 에러가 발생했습니다."

        price_list = data["RESULT"]["OIL"]

        message = f"*⛽ 제주시 휘발유 최저가 Top10 주유소*\n"
        for idx, item in enumerate(price_list):
            message += f"{idx+1}. {item['OS_NM']} / {item['PRICE']}원 / {item['NEW_ADR']}\n\n"
            
        print(f"{message}")
        return message
    except Exception as e:
        return f"데이터 가져오기 실패: {e}"

def send_to_slack(message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": SLACK_CHANNEL_ID,
        "text": message
    }

    r = requests.post(url, headers=headers, json=payload)
    res_data = r.json()
    if not res_data.get("ok"):
        print("❌ Slack 전송 실패:", res_data)
    else:
        print("✅ Slack 전송 성공!")

if __name__ == "__main__":
    # msg = get_gas_today_price()
    msg = get_gas_min_price()
    send_to_slack(msg)
