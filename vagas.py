import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

# Variáveis de ambiente (seguras via GitHub Secrets)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# Função para pontuar vaga com base no seu perfil
def calcular_score(vaga):
    titulo = vaga["title"].lower()
    descricao = vaga.get("description", "").lower()

    score = 0
    # 🔹 Hard skills principais
    if "flutter" in titulo or "flutter" in descricao:
        score += 4
    if "dart" in titulo or "dart" in descricao:
        score += 2
    if "mobile" in titulo or "mobile" in descricao:
        score += 2
    if "laravel" in titulo or "laravel" in descricao:
        score += 2
    if "mysql" in titulo or "mysql" in descricao:
        score += 1
    if "web" in titulo or "web" in descricao:
        score += 2
    if "developer" in titulo:
        score += 2

    # 🔹 Stack complementar
    if "infrastructure" in descricao or "it support" in descricao or "infra" in descricao:
        score += 1
    if "logistics" in descricao or "supply chain" in descricao or "e-commerce" in descricao:
        score += 1

    # 🔹 Idioma
    if "portuguese" in descricao or "brazil" in descricao:
        score += 2
    if "latam" in descricao:
        score += 2
    if "english fluent" in descricao or "advanced english" in descricao or "native english" in descricao:
        score -= 3

    # 🔹 Senioridade
    if "senior" in titulo or "staff" in titulo or "principal" in titulo or "lead" in titulo:
        score -= 3
    if "junior" in titulo or "mid" in titulo or "pleno" in titulo:
        score += 2

    # 🔹 Tipo de contratação
    if "deel" in descricao or "remote.com" in descricao or "oyster" in descricao or "eor" in descricao or "worldwide payroll" in descricao:
        score += 2

    # 🔹 Empresa menor
    tamanho = vaga.get("company_size", "").lower()
    if tamanho and any(x in tamanho for x in ["1-10", "11-50", "51-200", "201-500"]):
        score += 1

    return score


# Classificação por país
def classificar_pais(vaga):
    local = vaga.get("candidate_required_location", "").lower()

    if "brazil" in local or "latam" in local or "south america" in local:
        return "Brasil"
    elif "united states" in local or "usa" in local or "north america" in local:
        return "EUA"
    elif "worldwide" in local or "anywhere" in local or local == "":
        return "Demais localidades"
    else:
        return "Demais localidades"


# Probabilidade de chamada
def calcular_probabilidade(vaga, score):
    descricao = vaga.get("description", "").lower()

    if "portuguese" in descricao or "brazil" in vaga.get("candidate_required_location", "").lower():
        return "Alta"
    if score >= 6:
        return "Alta"
    elif 3 <= score < 6:
        return "Média"
    else:
        return "Baixa"


# Buscar vagas
def buscar_vagas():
    url = "https://remotive.com/api/remote-jobs"
    response = requests.get(url)
    data = response.json()

    vagas = []
    for vaga in data["jobs"]:
        score = calcular_score(vaga)
        pais = classificar_pais(vaga)
        prob = calcular_probabilidade(vaga, score)

        vagas.append({
            "titulo": vaga["title"],
            "empresa": vaga["company_name"],
            "link": vaga["url"],
            "pais": pais,
            "score": score,
            "probabilidade": prob
        })

    return vagas


# Montar corpo do e-mail
def montar_email(vagas):
    if not vagas:
        return "Nenhuma vaga encontrada hoje."

    # Organizar por país
    vagas_por_pais = {"EUA": [], "Brasil": [], "Demais localidades": []}
    for vaga in vagas:
        vagas_por_pais[vaga["pais"]].append(vaga)

    # Top 5
    top_5 = sorted(vagas, key=lambda x: x["score"], reverse=True)[:5]

    corpo = f"📌 Vagas encontradas em {datetime.now().strftime('%d/%m/%Y')}\n\n"

    # Listar por país
    for pais, lista in vagas_por_pais.items():
        corpo += f"🌎 {pais}\n"
        if lista:
            for v in sorted(lista, key=lambda x: x['score'], reverse=True)[:5]:
                corpo += f"- {v['titulo']} ({v['empresa']})\n  {v['link']}\n  Probabilidade: {v['probabilidade']} | Score: {v['score']}\n"
        else:
            corpo += "Nenhuma vaga encontrada.\n"
        corpo += "\n"

    # Top 5
    corpo += "⭐ Top 5 mais atrativas:\n"
    for v in top_5:
        corpo += f"- {v['titulo']} ({v['empresa']}) [{v['pais']}]\n  {v['link']}\n  Probabilidade: {v['probabilidade']} | Score: {v['score']}\n"

    return corpo


# Enviar e-mail
def enviar_email(corpo):
    msg = MIMEText(corpo, "plain")
    msg["Subject"] = f"Vagas de hoje - {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())


# Execução principal
if __name__ == "__main__":
    vagas = buscar_vagas()
    corpo = montar_email(vagas)
    enviar_email(corpo)
