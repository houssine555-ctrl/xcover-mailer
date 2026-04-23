import anthropic
import smtplib
import os
from email.mime.text import MIMEText
from datetime import date

XCOVER_EMAIL = "support@xcover.com"
FROM_EMAIL = "contact@aouayti.fr"
CLAIM_REF = "NGH8N-PCF6W-INS"
START_DATE = date(2026, 4, 23)

def get_day_number():
    return (date.today() - START_DATE).days + 1

def generate_email(day: int) -> str:
    if day <= 7:
        tone = "polite but firm"
    elif day <= 21:
        tone = "increasingly frustrated, mentioning legal options like ACPR"
    elif day <= 42:
        tone = "very insistent, explicitly threatening ACPR complaint and tribunal judiciaire"
    else:
        tone = "final warning, stating legal action is imminent"

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are writing email #{day} in an ongoing dispute with XCover insurance (claim ref: {CLAIM_REF}).

The situation: XCover refuses to reimburse a stolen Samsung Galaxy Book5 Pro laptop (capped at €250 under policy) by citing a checked baggage exclusion that literally does not exist anywhere in the contract. The policy explicitly covers electronic devices stolen during a trip (p.10/23), laptops are named in the glossary (p.17/23), and the only transport exclusion (p.11/23 point 22) covers shipped goods not airline checked baggage. They also previously reimbursed identical electronics in checked baggage under the same policy (claim 9R7GG-LEP47-CLA). They also forgot Timberland boots 220 euros, 2 years old despite invoice being submitted multiple times.

Total owed beyond what was paid: approximately 400 euros.

Tone for today (day {day}): {tone}

Write a short, direct email in English. No bullet points. No bold. Do not use em dashes. Vary the angle slightly from a standard complaint, mention a specific detail of the case to show this is not a template. Sign off as Houssine Aouayti."""
        }]
    )
    return message.content[0].text

def send_email(body: str, day: int):
    msg = MIMEText(body)
    msg["Subject"] = f"Claim {CLAIM_REF} — Follow-up #{day}"
    msg["From"] = FROM_EMAIL
    msg["To"] = XCOVER_EMAIL

    with smtplib.SMTP_SSL("smtp.protonmail.ch", 465) as server:
        server.login("contact@aouayti.fr", os.environ["PROTON_SMTP_TOKEN"])
        server.sendmail(FROM_EMAIL, XCOVER_EMAIL, msg.as_string())

if __name__ == "__main__":
    day = get_day_number()
    print(f"Day {day}")
    body = generate_email(day)
    print(body)
    send_email(body, day)
    print("Sent.")
