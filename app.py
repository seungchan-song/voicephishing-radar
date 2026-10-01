# Flask 웹
#   python app.py  ->  http://127.0.0.1:5000
# /      대시보드 (result.json)
# /news  뉴스 목록 (MongoDB news), /news?tag=기관사칭 처럼 수법으로 거르기
import os
import re
from flask import Flask, render_template, request
from markupsafe import Markup, escape
from common import load_result, won_to_eok
from config import TAGS, CHART_AGE, CHART_REGION, CHART_METHODS, CHART_YEARLY
from db import get_db

app = Flask(__name__)


@app.template_filter("emphasize")
def emphasize(text):
    # 문장 속 **강조할 말** 을 <strong>으로 바꾼다
    safe = str(escape(text))  # 먼저 안전하게 바꾼 뒤에 태그를 넣는다
    return Markup(re.sub(r"\*\*(.+?)\*\*", lambda m: "<strong>" + m.group(1) + "</strong>", safe))


@app.route("/")
def index():
    result = load_result()

    # 만들어진 그래프만 화면에 보여준다
    charts = []
    for path in [CHART_AGE, CHART_REGION, CHART_METHODS, CHART_YEARLY]:
        if os.path.exists(path):
            charts.append(path.replace("static/", ""))

    return render_template("index.html", result=result, charts=charts, eok=won_to_eok)


@app.route("/news")
def news():
    tag = request.args.get("tag", "")
    query = {}
    if tag in TAGS:
        query = {"tags": tag}

    error = None
    articles = []
    try:
        articles = list(get_db().news.find(query).sort("date", -1).limit(100))
    except Exception:
        error = "MongoDB에 연결할 수 없습니다. .env의 MONGO_URI를 확인하세요."

    return render_template("news.html", articles=articles, tags=TAGS, current=tag, error=error)


if __name__ == "__main__":
    app.run(debug=True)
