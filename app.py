from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import requests
import msal
import os
import pandas as pd
from jinja2 import Template

# Configurações do Azure
CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
TENANT_ID = "TENANT_ID"
REDIRECT_URI = "http://localhost:8000/auth/callback"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

# Criando o aplicativo FastAPI
app = FastAPI()

# Instância do MSAL para autenticação
msal_app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

# Armazena o token na memória (substituir por cache no futuro)
ACCESS_TOKEN = None

@app.get("/")
def home():
    return {"message": "API de Envio de Emails via Microsoft Graph"}

# Rota para iniciar a autenticação
@app.get("/auth/login")
def auth_login():
    auth_url = msal_app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)
    return RedirectResponse(auth_url)

# Callback após autenticação
@app.get("/auth/callback")
def auth_callback(code: str):
    global ACCESS_TOKEN
    token_response = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    
    if "access_token" in token_response:
        ACCESS_TOKEN = token_response["access_token"]
        return {"message": "Autenticação realizada com sucesso!"}
    else:
        raise HTTPException(status_code=400, detail="Erro na autenticação.")

# Função para carregar os destinatários do CSV
def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# Função para criar o template de e-mail
def create_email_template():
    with open("email_template.txt", "r", encoding="utf-8") as file:
        email_template = file.read()
        file.close()

    return Template(email_template)

# Rota para enviar e-mails
@app.post("/send-emails")
def send_emails():
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")

    # Ler CSV com destinatários
    file_path = "arquivo.csv"
    df = read_csv(file_path)

    # Criar template do e-mail
    template = create_email_template()

    for _, row in df.iterrows():
        email_content = template.render(nome=row["nome"], empresa=row["empresa"], cargo=row["cargo"])

        # Dados do e-mail para Microsoft Graph
        email_data = {
            "message": {
                "subject": "teste de automação",
                "body": {
                    "contentType": "Text",
                    "content": email_content
                },
                "toRecipients": [
                    {"emailAddress": {"address": row["email"]}}
                ]
            },
            "saveToSentItems": "true"
        }

        # Enviar e-mail via Microsoft Graph
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        response = requests.post("https://graph.microsoft.com/v1.0/me/sendMail", json=email_data, headers=headers)

        if response.status_code != 202:
            print(f"Erro ao enviar e-mail para {row['email']}: {response.text}")

    return {"message": "E-mails enviados com sucesso!"}

