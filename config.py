# 프로젝트 전체가 함께 쓰는 설정
# 비밀키는 .env 파일에서 읽는다. .env는 절대 깃허브에 올리지 않는다.
# 아래 약속된 값(태그, 연령대, 시도청)을 바꿔야 하면 톡방에 공유 부탁드립니다.
import os
from dotenv import load_dotenv

load_dotenv()

# ---- 비밀키 (.env) ----
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "voicephishing")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO", "")  # 여러 명이면 쉼표로 구분

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# ---- 파일 경로 (프로젝트 폴더에서 실행한다고 가정) ----
AGE_CSV = "data/raw/연령별.csv"
REGION_COUNT_CSV = "data/raw/지역별_건수.csv"
REGION_AMOUNT_CSV = "data/raw/지역별_금액.csv"
STATS_JSON = "data/processed/stats.json"
RESULT_JSON = "data/processed/result.json"

# 그래프 파일 (B2가 이 이름으로 저장하고, 웹과 메일이 이 이름으로 불러온다)
CHART_AGE = "static/charts/age.png"
CHART_REGION = "static/charts/region.png"
CHART_METHODS = "static/charts/methods.png"
CHART_YEARLY = "static/charts/yearly.png"

# ---- 약속된 값 (노션 "데이터 형식 약속") ----
TAGS = ["기관사칭", "가족·지인사칭", "대출빙자", "스미싱", "메신저피싱", "기타"]

AGE_GROUPS = ["20대이하", "30대", "40대", "50대", "60대", "70대이상"]

REGIONS = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기남부",
           "경기북부", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

NEWS_QUERIES = ["보이스피싱", "스미싱", "기관사칭", "메신저피싱"]

EOK = 100000000  # 1억 원. 금액 CSV(억원)를 원 단위로 바꿀 때 곱한다
