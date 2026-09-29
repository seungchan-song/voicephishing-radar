# [B3] result.json -> 가족에게 보내는 보이스피싱 경보 메일 (Gmail)
#   python mailer.py
#
# .env에 GMAIL_USER, GMAIL_APP_PASSWORD, MAIL_TO(쉼표로 여러 명)를 넣어야 한다.
# Gmail 앱 비밀번호는 구글 계정에서 2단계 인증을 켠 뒤 만들 수 있다.
import os
import smtplib
from email.message import EmailMessage
from common import load_result
from config import GMAIL_USER, GMAIL_APP_PASSWORD, MAIL_TO, CHART_METHODS


def make_body(result):
    # TODO(B3): 메일 본문(HTML 글자)을 만들어 돌려준다
    # 넣을 것: 수법 TOP 3 (result["top_methods"]의 name, count, sample의 title과 link)
    #         "이런 전화·문자는 무조건 끊으세요" 체크리스트
    pass


def send_mail(subject, body, image_path):
    # TODO(B3): EmailMessage로 메일을 만들어 Gmail(smtp.gmail.com, 465)로 보낸다
    # image_path 파일이 있으면 첨부한다
    pass


if __name__ == "__main__":
    result = load_result()
    subject = "[보이스피싱 레이더] 요즘 이런 수법을 조심하세요"
    if result["is_fake"]:
        subject = "[테스트] " + subject
    send_mail(subject, make_body(result), CHART_METHODS)
    print("메일 발송 완료:", MAIL_TO)
