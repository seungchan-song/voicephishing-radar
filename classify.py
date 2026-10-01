# [P2] news 기사마다 수법 태그(tags)를 붙인다
#   python classify.py
#
# 분류 태그:
# 기관사칭 / 가족·지인사칭 / 대출빙자 / 스미싱 / 메신저피싱 / 기타 / 무관
#
# 분류 원칙:
# 1. 예방·교육·홍보성 기사 -> 무관
# 2. 제목에서 구체적인 수법 확인 -> 해당 수법 태그
# 3. 제목에서 피싱 사건·피해는 확인되지만 수법 특정 불가 -> 기타
# 4. 제목만으로 피싱 기사인지 애매할 때만 본문을 보조적으로 확인
# 5. 본문의 단순 수법 나열만으로 특정 수법 태그를 붙이지 않음
# 6. 복수 태그 허용

import re
from db import get_db


KEYWORDS = {
    "기관사칭": [
        "검찰", "금감원", "수사관", "경찰",
        "공공기관", "관공서", "시청", "교도소",
        "소방기관", "소방서", "공무원", "재외공관"
    ],

    "가족·지인사칭": [
        "엄마", "아들", "딸",
        "액정 깨짐", "폰 고장"
    ],

    "대출빙자": [
        "저금리", "대환대출", "정부지원 대출",
        "대출 사기", "대출사기"
    ],

    "스미싱": [
        "스미싱", "택배", "청첩장", "부고",
        "과태료", "건강검진",
        "미끼문자", "미끼 문자"
    ],

    "메신저피싱": [
        "메신저피싱", "메신저 피싱",
        "카톡", "메신저", "상품권",
        "원격 앱", "원격앱"
    ],
}


PHISHING_WORDS = [
    "보이스피싱", "보이스 피싱",
    "전화금융사기", "전화 금융사기",
    "스미싱",
    "메신저피싱", "메신저 피싱",
    "피싱"
]


CRIME_WORDS = [
    "사칭", "사기",
    "피해", "피해액", "피해금",
    "송금", "입금", "현금",
    "검거", "구속", "징역",
    "탈취", "가로채",
    "범죄", "조직원",
    "악성앱", "악성 앱",
    "대포통장", "전달책",
    "입건", "편취"
]


# 제목에 아래 표현이 있으면 분석 제외
TITLE_EXCLUDE_WORDS = [
    "예방 캠페인",
    "예방 홍보",
    "예방 교육",
    "예방교육",
    "금융교육",
    "금융 교육",
    "금융소양교육",
    "금융소양 교육",
    "예방 맞손",
    "예방 간담회",
    "예방 대응 논의",
    "예방 이모티콘",

    "무료보험",
    "무료 보험",
    "보상보험",
    "보험 가입 행사",
    "보험 무료 제공",

    "감사장 수여",
    "감사장 전달",

    "홍보활동",
    "홍보 활동",

    "대응체계 가동",
    "대응 체계 가동",
    "차단 서비스",
    "사전 차단체계",
    "사전 차단 체계",

    "합수단 해체",
    "합수부도 문닫아",
    "합수부도 문 닫아",

    "2차피해 우려",
    "2차 피해 우려"
]


SMISHING_LURES = [
    "택배", "청첩장", "부고",
    "과태료", "건강검진",
    "미끼문자", "미끼 문자"
]


DIGITAL_ACTIONS = [
    "문자", "링크", "URL",
    "클릭", "눌렀", "누르",
    "악성앱", "악성 앱",
    "설치",
    "개인정보 탈취",
    "정보 탈취"
]


def is_excluded_title(title):
    """제목만으로 명확한 분석 제외 기사인지 확인한다."""

    if not title:
        return False

    return any(
        keyword in title
        for keyword in TITLE_EXCLUDE_WORDS
    )


def is_relevant(text):
    """문장이 실제 피싱 사건·피해·수법과 관련 있는지 확인한다."""

    if not text:
        return False

    # 구체적인 스미싱 수법
    has_smishing_lure = any(
        keyword in text
        for keyword in SMISHING_LURES
    )

    has_digital_action = any(
        keyword in text
        for keyword in DIGITAL_ACTIONS
    )

    if has_smishing_lure and has_digital_action:
        return True

    # 피싱 표현 + 실제 사건/피해 표현
    has_phishing = any(
        keyword in text
        for keyword in PHISHING_WORDS
    )

    has_crime = any(
        keyword in text
        for keyword in CRIME_WORDS
    )

    if has_phishing and has_crime:
        return True

    # 기관사칭
    if (
        any(
            keyword in text
            for keyword in KEYWORDS["기관사칭"]
        )
        and "사칭" in text
    ):
        return True

    # 일반 사칭 사건
    if (
        "사칭" in text
        and any(
            keyword in text
            for keyword in [
                "금전", "송금", "입금",
                "개인정보", "계정",
                "피해", "편취"
            ]
        )
    ):
        return True

    # 메신저피싱
    messenger_words = [
        "메신저피싱",
        "메신저 피싱",
        "카톡",
        "메신저"
    ]

    messenger_actions = [
        "상품권",
        "송금",
        "입금",
        "돈",
        "구매",
        "요구",
        "원격 앱",
        "원격앱"
    ]

    if (
        any(
            keyword in text
            for keyword in messenger_words
        )
        and any(
            keyword in text
            for keyword in messenger_actions
        )
    ):
        return True

    # 가족·지인사칭
    family = [
        "엄마", "아들", "딸",
        "액정 깨짐", "폰 고장"
    ]

    money = [
        "돈", "송금", "입금",
        "필요", "보내"
    ]

    if (
        any(keyword in text for keyword in family)
        and any(keyword in text for keyword in money)
    ):
        return True

    # 대출빙자
    if (
        any(
            keyword in text
            for keyword in KEYWORDS["대출빙자"]
        )
        and any(
            keyword in text
            for keyword in [
                "사기", "피해",
                "송금", "입금",
                "피싱", "문자"
            ]
        )
    ):
        return True

    # 대포통장 / 전달책 등 피싱 범죄 맥락
    phishing_crime_terms = [
        "대포통장",
        "전달책",
        "현금수거책",
        "현금 수거책"
    ]

    if (
        any(
            keyword in text
            for keyword in phishing_crime_terms
        )
        and any(
            keyword in text
            for keyword in [
                "보이스피싱",
                "피싱",
                "범죄조직",
                "범죄 조직",
                "사기"
            ]
        )
    ):
        return True

    if "미끼" in text and "피싱" in text:
        return True

    return False


def get_tags(text):
    """관련 문장에서 구체적인 수법 태그를 찾는다."""

    tags = []

    # 기관사칭
    if (
        any(
            keyword in text
            for keyword in KEYWORDS["기관사칭"]
        )
        and "사칭" in text
    ):
        tags.append("기관사칭")

    # 가족·지인사칭
    if any(
        keyword in text
        for keyword in KEYWORDS["가족·지인사칭"]
    ):
        tags.append("가족·지인사칭")

    # 대출빙자
    if any(
        keyword in text
        for keyword in KEYWORDS["대출빙자"]
    ):
        tags.append("대출빙자")

    # 스미싱
    if any(
        keyword in text
        for keyword in KEYWORDS["스미싱"]
    ):
        tags.append("스미싱")

    # 메신저피싱
    if any(
        keyword in text
        for keyword in KEYWORDS["메신저피싱"]
    ):
        tags.append("메신저피싱")

    return tags


def classify_article(title, body=""):
    """
    기사 1건을 최종 분류한다.

    1. 예방·교육·홍보성 제목 -> 무관
    2. 제목에서 구체적인 수법 확인 -> 수법 태그
    3. 제목에서 피싱 사건은 확인되지만 수법 특정 불가 -> 기타
    4. 제목이 애매할 때만 본문을 보조적으로 확인
    5. 끝까지 분석 대상이 아니면 무관
    """

    # 1. 제목 자체가 분석 제외 성격
    if is_excluded_title(title):
        return ["무관"]

    # 2. 제목에서 실제 피싱 사건/수법이 확인되는 경우
    if is_relevant(title):
        title_tags = get_tags(title)

        if title_tags:
            return title_tags

        # 피싱 관련 사건이지만 구체적 수법은 제목에서 확인되지 않음
        return ["기타"]

    # 3. 제목만으로 판단하기 어려운 경우에만 본문 확인
    sentences = re.split(
        r"[.!?。]\s*|\n+",
        body
    )

    found_tags = []
    found_relevant = False

    for sentence in sentences:
        if not is_relevant(sentence):
            continue

        found_relevant = True

        sentence_tags = get_tags(sentence)

        for tag in sentence_tags:
            if tag not in found_tags:
                found_tags.append(tag)

    if found_tags:
        return found_tags

    if found_relevant:
        return ["기타"]

    return ["무관"]


if __name__ == "__main__":
    db = get_db()

    count = 0

    for article in db.news.find():
        title = article.get("title", "")
        body = article.get("body", "")

        tags = classify_article(
            title,
            body
        )

        db.news.update_one(
            {"_id": article["_id"]},
            {"$set": {"tags": tags}}
        )

        count += 1

        if count % 100 == 0:
            print(
                f"태그 분류 중... {count}건 완료"
            )

    print(
        "태그 붙임:",
        count,
        "건"
    )
    