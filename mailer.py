# [B3] result.json -> 가족에게 보내는 보이스피싱 경보 메일 (네이버 메일)
#   python mailer.py
#
# .env에 MAIL_USER, MAIL_PASSWORD, MAIL_TO(쉼표로 여러 명)를 넣어야 한다.
# 네이버 메일 설정에서 IMAP/SMTP 사용을 켜야 한다. 2단계 인증을 쓰면 애플리케이션 비밀번호를 넣는다.
import html
import os
import smtplib
from email.message import EmailMessage
from common import load_result
from config import MAIL_USER, MAIL_PASSWORD, MAIL_TO, DASHBOARD_URL

def make_body(result):
    # 메일 본문(HTML 글자)을 만들어 돌려준다
    # 넣을 것: 수법 TOP 3 (result["top_methods"]의 name, count, sample의 title과 link)
    #         "이런 전화·문자는 무조건 끊으세요" 체크리스트
    top_methods = result.get("top_methods", [])
    
    # 1. 수법 TOP 3 HTML 목록 생성
    methods_html = ""
    for item in top_methods:
        rank = item.get("rank", "")
        name = html.escape(item.get("name", ""))  # 기사 제목 속 < > 가 HTML로 해석되지 않게 바꾼다
        count = item.get("count", 0)
        sample = item.get("sample", {})
        title = html.escape(sample.get("title", ""))
        link = html.escape(sample.get("link", "#"))
        
        methods_html += f"""
        <li style="margin-bottom: 15px; padding: 12px; background-color: #f9f9f9; border-left: 4px solid #d9534f; list-style: none;">
            <strong style="font-size: 16px; color: #333;">[{rank}위] {name}</strong> 
            <span style="color: #666; font-size: 14px;">({count}건 보도)</span><br>
            <span style="font-size: 14px; color: #555;">최근 기사: </span>
            <a href="{link}" target="_blank" style="color: #0275d8; text-decoration: none; font-weight: bold;">{title}</a>
        </li>
        """

    # 2. 전체 HTML 메일 본문 구성 (체크리스트 포함)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #d9534f; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 22px;">🚨 [보이스피싱 레이더] 경보 메일</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px;">최근 유행하는 보이스피싱 수법을 확인하고 피해를 예방하세요!</p>
        </div>
        
        <div style="border: 1px solid #ddd; border-top: none; padding: 20px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #d9534f; font-size: 18px; border-bottom: 2px solid #d9534f; padding-bottom: 8px;">📊 최근 유행 수법 TOP 3</h2>
            <ul style="padding-left: 0; margin-top: 15px;">
                {methods_html}
            </ul>

            <div style="margin-top: 30px; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 8px;">
                <h3 style="margin-top: 0; color: #856404; font-size: 16px;">🛑 "이런 전화·문자는 무조건 끊으세요!" 체크리스트</h3>
                <ul style="margin: 0; padding-left: 20px; color: #856404; font-size: 14px;">
                    <li style="margin-bottom: 8px;"><strong>검찰·경찰·금감원 사칭:</strong> 계좌 이체나 현금 인출을 요구하면 100% 사기입니다.</li>
                    <li style="margin-bottom: 8px;"><strong>가족·지인 사칭:</strong> '엄마 폰 고장났어' 등 액정 깨짐/원격 앱 설치 문자는 본인 직접 전화로 확인하세요.</li>
                    <li style="margin-bottom: 8px;"><strong>저금리 대환대출:</strong> 기존 대출금을 먼저 상환하라고 요구하는 것은 피싱 수법입니다.</li>
                    <li><strong>택배·청첩장·부고 문자:</strong> 출처가 불분명한 문자 속 인터넷 주소(URL)는 절대로 클릭하지 마세요.</li>
                </ul>
            </div>

            <div style="margin-top: 24px; text-align: center;">
                <a href="{DASHBOARD_URL}" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #4f46e5; color: white; text-decoration: none; font-weight: bold; border-radius: 8px;">📊 대시보드에서 더 자세히 보기</a>
            </div>

            <hr style="border: none; border-top: 1px solid #eee; margin: 25px 0;">
            <p style="font-size: 12px; color: #888; text-align: center;">
                본 메일은 보이스피싱 레이더 자동화 시스템에 의해 발송되었습니다.
            </p>
        </div>
    </body>
    </html>
    """
    return html_content

def send_mail(subject, body, image_path):
    # EmailMessage로 메일을 만들어 네이버 메일(smtp.naver.com, 465)로 보낸다
    # image_path 파일이 있으면 첨부한다
    # 받는 사람은 쉼표로 나눠서 리스트로 만든다 (공백, 빈 칸은 버린다)
    to_list = []
    for address in MAIL_TO.split(","):
        if address.strip():
            to_list.append(address.strip())
    if not to_list or not MAIL_USER or not MAIL_PASSWORD:
        raise ValueError(".env에 MAIL_USER, MAIL_PASSWORD, MAIL_TO를 모두 넣어야 합니다.")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = MAIL_USER
    msg['To'] = ", ".join(to_list)

    # HTML 본문 설정
    msg.set_content(body, subtype='html', charset='utf-8')

    # 그래프 이미지 파일이 존재하는 경우 첨부
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            img_data = f.read()
            msg.add_attachment(
                img_data,
                maintype='image',
                subtype='png',
                filename=os.path.basename(image_path)
            )

    # 네이버 SSL 서버 접속 및 메일 발송 (포트 465)
    with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
        server.login(MAIL_USER, MAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    result = load_result()
    subject = "[보이스피싱 레이더] 요즘 이런 수법을 조심하세요"
    if result["is_fake"]:
        subject = "[테스트] " + subject
    send_mail(subject, make_body(result), None)  # 그래프는 첨부하지 않는다 (대시보드에서 확인)
    print("메일 발송 완료:", MAIL_TO)