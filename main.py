import os
from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "minha_senha_super_secreta_123")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="HubPlace AI SDR Agent",
    version="1.0.0"
)

# Validador de Segurança da API Key
def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: Chave de API inválida ou ausente."
        )
    return x_api_key

# Estrutura de dados esperada para novos leads
class LeadNewRequest(BaseModel):
    name: str
    email: EmailStr
    company: str
    role: str
    segment: str

@app.get("/")
def home():
    return {"status": "online", "message": "Agente de IA da HubPlace rodando com sucesso!"}

@app.post("/api/leads/new")
def new_lead_welcome(payload: LeadNewRequest, x_api_key: str = Header(None)):
    # Valida a segurança
    verify_api_key(x_api_key)
    
    try:
        # Prompt para a IA gerar o e-mail de apresentação personalizado
        prompt = f"""
        Você é o SDR especialista em IA da HubPlace.com (plataforma B2B de contratação de tecnologia e fornecedores via IA).
        Escreva um e-mail de prospecção B2B altamente personalizado para {payload.name}, que atua como {payload.role} na empresa {payload.company}, focada no segmento de {payload.segment}.
        Mostre como a HubPlace resolve demandas de tecnologia em até 48h com curadoria e IA.
        Retorne estritamente em formato JSON com as chaves: "subject" e "body".
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        email_content = json.loads(response.choices[0].message.content)
        
        return {
            "status": "success",
            "email_generated": email_content,
            "hubspot_action": {
                "email": payload.email,
                "hubspot_deal_stage": "E-mail de Apresentação Enviado",
                "source": "HubPlace AI Agent"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro ao processar a IA: {str(e)}"
        )