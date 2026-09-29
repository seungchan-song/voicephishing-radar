# result.json 읽기/쓰기. 그래프·웹·메일·Notion 담당은 load_result()만 쓰면 된다.
import json
from config import RESULT_JSON


def load_result():
    with open(RESULT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_result(result):
    # ensure_ascii=False: 한글을 그대로 저장
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def won_to_eok(amount):
    # 원 단위 금액을 화면용 글자로 바꾼다. 예: 402800000000 -> "4,028억 원"
    if amount is None:
        return "-"
    return f"{amount // 100000000:,}억 원"
