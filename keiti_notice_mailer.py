print("스크립트 시작")

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

# 날짜 범위
today = datetime.today()
yesterday = today - timedelta(days=1)

# KEITI 공지사항 페이지
URL = "https://www.keiti.re.kr/site/keiti/ex/board/List.do?cbIdx=277"
res = requests.get(URL)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

rows = soup.select("div.bbsList tbody tr")
print(f"rows found: {len(rows)}")

new_posts = []
for row in rows:
    cols = row.find_all("td")
    date_text = cols[3].text.strip()  # 게시일
    try:
        post_date = datetime.strptime(date_text, "%Y-%m-%d")
    except:
        continue

    if post_date.date() == today.date() or post_date.date() == yesterday.date():
        title = cols[1].text.strip()
        link = "https://www.keiti.re.kr" + cols[1].find("a")["href"]
        new_posts.append(f"{post_date.date()} - {title}\n{link}")

if new_posts:
    print(f"📌 새 게시물 발견 {len(new_posts)}건")
    body = "\n\n".join(new_posts)
    msg = MIMEText(body)
    msg["Subject"] = f"[KEITI] 새 공지사항 {len(new_posts)}건 ({today.strftime('%Y-%m-%d')})"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_TO"]

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
            smtp.send_message(msg)
        print("✅ 이메일 발송 성공")
    except Exception as e:
        print("❌ 이메일 발송 실패:", e)
else:
    print("🔎 새 게시물이 없습니다.")