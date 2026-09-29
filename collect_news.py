# [P2] 네이버 뉴스 API + 구글 뉴스 RSS -> MongoDB news 컬렉션
#   python collect_news.py
#
# 저장할 문서 모양 (노션 "데이터 형식 약속 -> news")
#   {"title": "...", "date": "2026-09-20", "link": "https://...", "body": "", "source": "naver", "tags": []}
# - title: <b> 같은 HTML 태그는 지운다
# - date: "YYYY-MM-DD" 글자
# - body: 네이버 기사(n.news.naver.com)만 본문 앞부분, 나머지는 ""
# - source: "naver" 또는 "google"
# - tags: 여기서는 빈 리스트 [], classify.py가 채운다
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NEWS_QUERIES
from db import get_db, create_indexes

NAVER_URL = "https://openapi.naver.com/v1/search/news.json"
GOOGLE_RSS = "https://news.google.com/rss/search?q={}&hl=ko&gl=KR&ceid=KR:ko"


def fetch_naver(query):
    # TODO(P2): 네이버 API로 기사를 받아 문서 리스트로 돌려준다 (sort=date, display=100, start 1~1000)
    pass


def fetch_google(query):
    # TODO(P2): feedparser로 구글 RSS를 읽어 문서 리스트로 돌려준다 (body는 "")
    pass


def crawl_body(url):
    # TODO(P2): n.news.naver.com 기사 본문 앞부분을 돌려준다. 실패하면 ""
    # 요청 사이에 time.sleep(1)
    pass


def save(articles):
    # 같은 link가 이미 있으면 건너뛴다. 새로 저장한 개수를 돌려준다
    db = get_db()
    saved = 0
    for article in articles:
        if db.news.find_one({"link": article["link"]}) is None:
            db.news.insert_one(dict(article))
            saved += 1
    return saved


if __name__ == "__main__":
    create_indexes()
    total = 0
    for query in NEWS_QUERIES:
        total += save(fetch_naver(query))
        total += save(fetch_google(query))
    print("news 새로 저장:", total, "건")
