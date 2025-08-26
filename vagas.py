import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

# Variáveis de ambiente (segurança no GitHub Actions)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # senha de app do Gmail
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def buscar_vagas():
    url = "https://remotive.com/api/remote-jobs"
    response = requests.get(url)
    data = response.json()

    vagas_filtradas = []
    for vaga in data["jobs"]:
        titulo = vaga["title"]
        empresa = vaga["company_name"]
        link = vaga["url"]

        # Filtros básicos: área + salário
        if any(keyword in titulo.lower() for keyword in ["flutter", "developer", "software", "ti"]):
            # Remotive não sempre traz salário, mas podemos adicionar outros portais depois
            vagas_filtradas.append(f"{titulo} - {empresa}\n{link}\n")

    return vagas_filtradas

def enviar_email(vagas):
    if not vagas:
        corpo = "Nenhuma vaga encontrada hoje."
    else:
        corpo = "Vagas encontradas:\n\n" + "\n".join(vagas)

    msg = MIMEText(corpo, "plain")
    msg["Subject"] = f"Vagas de hoje - {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

if __name__ == "__main__":
    vagas = buscar_vagas()
    enviar_email(vagas)
