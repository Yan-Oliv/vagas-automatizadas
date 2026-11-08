# Vagas Automatizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white) ![Automação](https://img.shields.io/badge/Automação-f18a4b?style=flat-square)

Robô que **busca vagas de desenvolvimento todos os dias**, pontua cada vaga pelo meu perfil técnico e envia um resumo por **e-mail**. Roda sozinho no GitHub Actions.

## Como funciona

1. Consulta fontes de vagas (APIs da **Jooble**, **Adzuna** e Google Jobs via **SerpAPI**).
2. Calcula um *score* por palavras-chave (Flutter, Dart, Laravel, MySQL, mobile, web…).
3. Ordena as melhores e envia por SMTP (Gmail).

O workflow `.github/workflows/vagas.yml` roda diariamente às 06h (BRT) e também manualmente (`workflow_dispatch`).

## Configuração

Cadastre os segredos em **Settings → Secrets and variables → Actions**:

| Segredo | Uso |
|---|---|
| `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER` | envio do resumo por e-mail |
| `JOOBLE_API_KEY` | API da Jooble |
| `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | API da Adzuna |
| `SERPAPI_KEY` | Google Jobs via SerpAPI |

> As chaves das APIs também precisam ser repassadas no bloco `env` do passo *Run vagas.py* do workflow.

## Executar localmente

```bash
pip install -r requirements.txt
python vagas.py   # com as variáveis acima no ambiente
```

---

<sub>Desenvolvido por <a href="https://github.com/Yan-Oliv">Yan Monteiro</a> · <a href="https://www.linkedin.com/in/yan-de-oliveira-gon%C3%A7alves-monteiro-a2886619a/">LinkedIn</a> · <a href="https://github.com/OmnyaTech">OmnyaTech</a></sub>
