import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BRVM_URL = "https://www.brvm.org/fr/marche/bulletin-officiel-de-la-cote"

EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECEIVERS = os.environ["EMAIL_RECEIVERS"].split(",")

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_latest_bulletin_url():
    r = requests.get(BRVM_URL, headers=HEADERS, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    link = soup.find("a", string=lambda x: x and "Télécharger" in x)
    if not link:
        raise Exception("Lien de téléchargement introuvable")

    pdf_url = link.get("href")
    if pdf_url.startswith("/"):
        pdf_url = "https://www.brvm.org" + pdf_url

    return pdf_url


def download_bulletin(url):
    filename = f"Bulletin_BRVM_{datetime.now().strftime('%Y%m%d')}.pdf"
    r = requests.get(url, headers=HEADERS, verify=False)

    with open(filename, "wb") as f:
        f.write(r.content)

    return filename


def send_email(pdf_file):
    msg = EmailMessage()
    msg["Subject"] = "📈 Bulletin Officiel de la Cote BRVM"
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVERS)

    msg.set_content(
        "Bonjour,\n\n"
        "Veuillez trouver en pièce jointe le Bulletin Officiel de la Cote BRVM.\n\n"
        "Cordialement."
    )

    with open(pdf_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=pdf_file
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)


def main():
    url = get_latest_bulletin_url()
    pdf = download_bulletin(url)
    send_email(pdf)


if __name__ == "__main__":
    main()
