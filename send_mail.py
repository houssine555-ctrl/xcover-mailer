import anthropic
import smtplib
import os
import random
from email.mime.text import MIMEText
from datetime import date

FROM_EMAIL = "contact@aouayti.fr"
XCOVER_EMAIL = "support@xcover.com"
CLAIM_REF = "RTTNK-6JG33-CLA"
POLICY_REF = "NGH8N-PCF6W-INS"
START_DATE = date(2026, 4, 23)

LANGUAGES = [
    "English", "Mandarin Chinese", "Spanish",
    "French", "Arabic", "Portuguese", "Korean", "Japanese"
]

ANGLES = [
    "Focus on the fact that the exclusion doesn't exist in the contract and ask them to cite the exact clause and page number.",
    "Focus on the inconsistency with the previous claim 9R7GG-LEP47-CLA where identical electronics in checked baggage were reimbursed.",
    "Focus on the fact that the bag was forcibly checked at the gate by Delta, not a choice made by the customer.",
    "Focus on the Timberland boots being ignored despite multiple invoice submissions.",
    "Focus on the arithmetic error in their decision and the lack of professionalism it demonstrates.",
    "Focus on the overall timeline — several months without resolution — and the impact on the customer.",
    "Focus on the contradiction between their glossary defining laptops as covered electronic devices and their refusal to pay.",
    "Focus on the point 22 exclusion applying only to shipped goods, not airline checked baggage, and how their interpretation is legally incorrect.",
]

def get_day_number():
    return (date.today() - START_DATE).days + 1

def generate_email(day: int, slot: str) -> tuple:
    if day <= 3:
    tone = "polite but firm"
elif day <= 7:
    tone = "increasingly frustrated, hinting at legal options"
elif day <= 14:
    tone = "very insistent, explicitly mentioning ACPR complaint and tribunal judiciaire"
else:
    tone = "final warning, stating legal action is imminent"

    language = random.choice(LANGUAGES)
    angle = random.choice(ANGLES)

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are writing email #{day} ({slot} send) in an ongoing dispute with XCover insurance.

Claim ref: {CLAIM_REF}
Policy ref: {POLICY_REF}

Background: XCover refuses to reimburse a stolen Samsung Galaxy Book5 Pro laptop (capped at 250 euros under policy) by citing a checked baggage exclusion that does not exist anywhere in the contract. The policy explicitly covers electronic devices stolen during a trip (p.10/23), laptops are named in the glossary (p.17/23), and the only transport exclusion (p.11/23 point 22) covers shipped goods only. They also previously reimbursed identical electronics in checked baggage under the same policy (claim 9R7GG-LEP47-CLA). Timberland boots (220 euros, 2 years old) also ignored despite invoice submitted multiple times. Total owed: approximately 400 euros.

Tone: {tone}
Angle for this email: {angle}
Write the email in: {language}

Write a short, direct email. No bullet points. No bold. No em dashes. Sign off as Houssine Aouayti. Return only the email body, no subject line."""
        }]
    )

    subject = f"Claim {CLAIM_REF} / Policy {POLICY_REF} — Follow-up #{day} ({slot})"
    return subject, message.content[0].text, language

def send_email(subject: str, body: str, day: int):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = XCOVER_EMAIL

    with smtplib.SMTP_SSL("smtp.protonmail.ch", 465) as server:
        server.login("contact@aouayti.fr", os.environ["PROTON_SMTP_TOKEN"])
        server.sendmail(FROM_EMAIL, XCOVER_EMAIL, msg.as_string())

if __name__ == "__main__":
    slot = os.environ.get("SLOT", "day")
    day = get_day_number()
    print(f"Day {day} — Slot: {slot}")
    subject, body, language = generate_email(day, slot)
    print(f"Language: {language}")
    print(body)
    send_email(subject, body, day)
    print("Sent.")
