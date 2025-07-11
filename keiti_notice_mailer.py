print("📦 KEITI 공지사항 스크립트 시작")

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

today = datetime.today()
last_week = today - timedelta(days=7)

URL = "https://www.keiti.re.kr/site/keiti/ex/board/List.do?cbIdx=277"
res = requests.get(URL)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

rows = soup.select("table.bbsDefault > tbody > tr")
print(f"🔎 rows found: {len(rows)}")

new_posts = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 3:
        continue
    title_tag = cols[1].find("a")
    date_text = cols[2].get_text(strip=True)
    post_date = datetime.strptime(date_text, "%Y-%m-%d")

    if post_date >= last_week:
        title = title_tag.get_text(strip=True)
        href = title_tag['href']
        link = "https://www.keiti.re.kr" + href
        new_posts.append(f"{post_date.date()} - {title}\n{link}")

# 이메일 전송
if new_posts:
    msg_body = "\n\n".join(new_posts)
    msg = MIMEText(msg_body)
    msg["Subject"] = f"KEITI 공지사항 주간 알림 ({today.strftime('%Y-%m-%d')})"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_TO"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
        smtp.send_message(msg)
        print("📨 메일 발송 완료")
else:
    print("📭 최근 1주일 게시물이 없어 메일을 보내지 않습니다.")
