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
from email.utils import parsedate_to_datetime

# 네이버 뉴스 API 주소와 구글 뉴스 RSS 주소
NAVER_URL = "https://naverapihub.apigw.ntruss.com/search/v1/news"
GOOGLE_RSS = "https://news.google.com/rss/search?q={}&hl=ko&gl=KR&ceid=KR:ko"


def fetch_naver(query):
    # 네이버 API로 기사를 받아 문서 리스트로 돌려준다 (sort=date, display=100, start 1~1000)

    # 네이버 API 인증 정보
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
    }

    articles = []

    # 한 번에 100건씩 요청하여 검색어당 최대 1,000건까지 수집
    for start in range(1, 1001, 100):
        print(f"[네이버] '{query}' 수집 중... {start}/1000")

        params = {
            "query": query,
            "display": 100,
            "start": start,
            "sort": "date",
            "format": "json",
        }

        # 네이버 뉴스 API에 기사 검색 요청
        response = requests.get(
            NAVER_URL,
            headers=headers,
            params=params,
            timeout=10
        )

        # 요청 실패 시 오류를 발생시키고, 성공하면 JSON으로 변환
        response.raise_for_status()
        data = response.json()

        # 받아온 기사들을 MongoDB에 저장할 형태로 정리
        for item in data["items"]:
            # 제목의 HTML 태그 제거
            title = BeautifulSoup(item["title"], "html.parser").get_text()

            # 기사 날짜를 YYYY-MM-DD 형식으로 변환
            date = parsedate_to_datetime(item["pubDate"]).strftime("%Y-%m-%d")

            link = item["link"]

            # 네이버 뉴스 기사인 경우 본문 앞부분 수집
            body = crawl_body(link)

            articles.append({
                "title": title,
                "date": date,
                "link": link,
                "body": body,
                "source": "naver",
                "tags": [],
            })

        # 100건보다 적게 왔다면 더 이상 검색 결과가 없으므로 종료
        if len(data["items"]) < 100:
            break

    return articles


def fetch_google(query):
    # feedparser로 구글 RSS를 읽어 문서 리스트로 돌려준다 (body는 "")
    print(f"[구글] '{query}' RSS 수집 중...")

    # 검색어를 넣어 구글 뉴스 RSS를 읽어옴
    feed = feedparser.parse(GOOGLE_RSS.format(query))

    articles = []

    # RSS에서 받은 기사들을 MongoDB에 저장할 형태로 정리
    for entry in feed.entries:
        # 기사 날짜를 YYYY-MM-DD 형식으로 변환
        date = parsedate_to_datetime(entry.published).strftime("%Y-%m-%d")

        articles.append({
            "title": entry.title,
            "date": date,
            "link": entry.link,
            "body": "",
            "source": "google",
            "tags": [],
        })

    return articles


def crawl_body(url):
    # n.news.naver.com 기사 본문 앞부분을 돌려준다. 실패하면 ""
    # 요청 사이에 time.sleep(1)

    # 네이버 뉴스 기사가 아니면 본문을 수집하지 않음
    if "n.news.naver.com" not in url:
        return ""

    try:
        # 연속 요청을 피하기 위해 기사마다 1초 대기
        time.sleep(1)

        # 네이버 뉴스 기사 페이지 요청
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.raise_for_status()

        # HTML에서 실제 기사 본문 영역 찾기
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.select_one("#dic_area")

        # 본문을 찾지 못하면 빈 문자열 반환
        if body is None:
            return ""

        # HTML 태그를 제거하고 본문을 일반 문자열로 변환
        text = body.get_text(" ", strip=True)

        # 본문이 너무 길어지지 않도록 앞 2,000자만 사용
        return text[:2000]

    # 기사 요청에 실패하더라도 전체 수집은 계속 진행
    except requests.RequestException:
        return ""


def save(articles):
    # 같은 link가 이미 있으면 건너뛴다. 새로 저장한 개수를 돌려준다
    db = get_db()
    saved = 0

    # 수집한 기사를 하나씩 확인
    for article in articles:

        # 같은 링크가 DB에 없을 때만 새로 저장
        if db.news.find_one({"link": article["link"]}) is None:
            db.news.insert_one(dict(article))
            saved += 1

    return saved


if __name__ == "__main__":
    # MongoDB 인덱스 생성
    create_indexes()
    total = 0

    # config.py에 정의된 검색어를 하나씩 수집
    for query in NEWS_QUERIES:
        print(f"\n===== '{query}' 수집 시작 =====")

        # 네이버 뉴스와 구글 뉴스 수집 후 새로 저장된 기사 수 누적
        total += save(fetch_naver(query))
        total += save(fetch_google(query))

    print("\nnews 새로 저장:", total, "건")
    