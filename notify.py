import os, smtplib, ssl, requests
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from zoneinfo import ZoneInfo

KEYWORDS = ["Div. 4", "Div. 3", "Educational", "Div. 2"]
WINDOW_HOURS = 24 * 14   # looks 14 days ahead for testing; change to 24 later
IST = ZoneInfo("Asia/Kolkata")

def upcoming_beginner_contests():
    data = requests.get("https://codeforces.com/api/contest.list", timeout=30).json()
    now = datetime.now(timezone.utc)
    limit = now + timedelta(hours=WINDOW_HOURS)
    found = []
    for c in data["result"]:
        if c["phase"] != "BEFORE":
            continue
        start = datetime.fromtimestamp(c["startTimeSeconds"], timezone.utc)
        if now <= start < limit and any(k.lower() in c["name"].lower() for k in KEYWORDS):
            found.append((c, start))
    return found

def send_email(body):
    msg = EmailMessage()
    msg["Subject"] = "Codeforces beginner contest coming up"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(os.environ["EMAIL_USER"], os.environ["EMAIL_APP_PASSWORD"])
        s.send_message(msg)

if __name__ == "__main__":
    contests = upcoming_beginner_contests()
    if not contests:
        print("No matching contests in the time window.")
    else:
        lines = []
        for c, start in contests:
            local = start.astimezone(IST).strftime("%a %d %b, %I:%M %p IST")
            hours = c["durationSeconds"] / 3600
            lines.append(f"{c['name']}\n  Starts: {local}  |  Duration: {hours:.1f}h\n"
                         f"  https://codeforces.com/contests/{c['id']}\n")
        text = "\n".join(lines)
        print(text)                      # this is what you'll see in the results
        if os.environ.get("EMAIL_USER"): # only email if you've set up email
            send_email(text)
            print("Email sent.")
        else:
            print("Email not set up yet, so no email was sent.")
