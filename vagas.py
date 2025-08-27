import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os
from serpapi import GoogleSearch

# Variáveis seguras (GitHub Secrets)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")


# ---------------- Regras de Score ---------------- #
def calcular_score(vaga):
    titulo = vaga["title"].lower() if vaga.get("title") else ""
    descricao = vaga.get("description", "").lower()

    score = 0
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

    if "infrastructure" in descricao or "it support" in descricao or "infra" in descricao:
        score += 1
    if "logistics" in descricao or "supply chain" in descricao or "e-commerce" in descricao:
        score += 1

    if "portuguese" in descricao or "brazil" in descricao:
        score += 2
    if "latam" in descricao:
        score += 2
    if "english fluent" in descricao or "advanced english" in descricao or "native english" in descricao:
        score -= 3

    if "senior" in titulo or "staff" in titulo or "principal" in titulo or "lead" in titulo:
        score -= 3
    if "junior" in titulo or "mid" in titulo or "pleno" in titulo:
        score += 2

    if "deel" in descricao or "remote.com" in descricao or "oyster" in descricao or "eor" in descricao:
        score += 2

    tamanho = vaga.get("company_size", "").lower()
    if tamanho and any(x in tamanho for x in ["1-10", "11-50", "51-200", "201-500"]):
        score += 1

    return score


def classificar_pais(vaga):
    local = vaga.get("candidate_required_location", "").lower()
    if "brazil" in local or "latam" in local or "south america" in local or "brasil" in local:
        return "Brasil"
    elif "united states" in local or "usa" in local or "north america" in local:
        return "EUA"
    elif "worldwide" in local or "anywhere" in local or local == "":
        return "Demais localidades"
    else:
        return "Demais localidades"


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


# ---------------- Normalização ---------------- #
def normalizar_vaga(vaga, origem):
    if origem == "remotive":
        return {
            "title": vaga["title"],
            "company": vaga["company_name"],
            "url": vaga["url"],
            "description": vaga.get("description", ""),
            "candidate_required_location": vaga.get("candidate_required_location", ""),
            "company_size": vaga.get("company_size", "")
        }
    elif origem == "jooble":
        return {
            "title": vaga["title"],
            "company": vaga["company"],
            "url": vaga["link"],
            "description": vaga.get("snippet", ""),
            "candidate_required_location": vaga.get("location", ""),
            "company_size": ""
        }
    elif origem == "adzuna":
        return {
            "title": vaga["title"],
            "company": vaga["company"]["display_name"] if vaga.get("company") else "Desconhecida",
            "url": vaga["redirect_url"],
            "description": vaga.get("description", ""),
            "candidate_required_location": vaga.get("location", {}).get("display_name", ""),
            "company_size": ""
        }
    elif origem == "google_jobs":
        return {
            "title": vaga.get("title"),
            "company": vaga.get("company_name", "Desconhecida"),
            "url": vaga.get("related_links", [{}])[0].get("link"),
            "description": vaga.get("description", ""),
            "candidate_required_location": vaga.get("location", ""),
            "company_size": ""
        }


# ---------------- Fontes ---------------- #
def buscar_vagas_remotive():
    vagas = []
    try:
        resp = requests.get("https://remotive.com/api/remote-jobs").json()
        for v in resp["jobs"]:
            vagas.append(normalizar_vaga(v, "remotive"))
    except Exception as e:
        print("Erro Remotive:", e)
    return vagas


def buscar_vagas_jooble():
    vagas = []
    if not JOOBLE_API_KEY:
        return vagas
    try:
        resp = requests.post(f"https://jooble.org/api/{JOOBLE_API_KEY}",
                             json={"keywords": "flutter", "location": "Brazil"}).json()
        for v in resp.get("jobs", []):
            vagas.append(normalizar_vaga(v, "jooble"))
    except Exception as e:
        print("Erro Jooble:", e)
    return vagas


def buscar_vagas_adzuna():
    vagas = []
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return vagas
    try:
        resp = requests.get(
            f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&what=flutter"
        ).json()
        for v in resp.get("results", []):
            vagas.append(normalizar_vaga(v, "adzuna"))
    except Exception as e:
        print("Erro Adzuna:", e)
    return vagas


def buscar_vagas_google(query="flutter"):
    vagas = []
    if not SERPAPI_KEY:
        return vagas
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": "Brazil",
        "hl": "pt",
        "gl": "br",
        "api_key": SERPAPI_KEY,
        "chips": "employment_type:full_time,remote:true",
        "start": 0
    }
    try:
        resultados = GoogleSearch(params).get_dict()
        for v in resultados.get("jobs_results", []):
            vagas.append(normalizar_vaga(v, "google_jobs"))
    except Exception as e:
        print("Erro Google Jobs:", e)
    return vagas


# ---------------- Busca unificada ---------------- #
def buscar_vagas():
    todas = []
    todas += buscar_vagas_remotive()
    todas += buscar_vagas_jooble()
    todas += buscar_vagas_adzuna()
    todas += buscar_vagas_google()

    resultado = []
    for vaga in todas:
        score = calcular_score(vaga)
        pais = classificar_pais(vaga)
        prob = calcular_probabilidade(vaga, score)
        resultado.append({
            "titulo": vaga["title"],
            "empresa": vaga["company"],
            "link": vaga["url"],
            "pais": pais,
            "score": score,
            "probabilidade": prob
        })
    return resultado


# ---------------- Email ---------------- #
def montar_email(vagas):
    if not vagas:
        return "Nenhuma vaga encontrada hoje."

    vagas_por_pais = {"EUA": [], "Brasil": [], "Demais localidades": []}
    for vaga in vagas:
        vagas_por_pais[vaga["pais"]].append(vaga)

    top_5 = sorted(vagas, key=lambda x: x["score"], reverse=True)[:5]
    corpo = f"📌 Vagas encontradas em {datetime.now().strftime('%d/%m/%Y')}\n\n"

    for pais, lista in vagas_por_pais.items():
        corpo += f"🌎 {pais}\n"
        if lista:
            for v in sorted(lista, key=lambda x: x['score'], reverse=True)[:5]:
                corpo += f"- {v['titulo']} ({v['empresa']})\n  {v['link']}\n  Probabilidade: {v['probabilidade']} | Score: {v['score']}\n"
        else:
            corpo += "Nenhuma vaga encontrada.\n"
        corpo += "\n"

    corpo += "⭐ Top 5 mais atrativas:\n"
    for v in top_5:
        corpo += f"- {v['titulo']} ({v['empresa']}) [{v['pais']}]\n  {v['link']}\n  Probabilidade: {v['probabilidade']} | Score: {v['score']}\n"
    return corpo


def enviar_email(corpo):
    msg = MIMEText(corpo, "plain")
    msg["Subject"] = f"Vagas de hoje - {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())


# ---------------- Main ---------------- #
if __name__ == "__main__":
    vagas = buscar_vagas()
    corpo = montar_email(vagas)
    enviar_email(corpo)
