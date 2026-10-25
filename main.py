import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# Configura a API Key do Gemini através da variável de ambiente no Render
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

app = FastAPI()

class LeadInput(BaseModel):
    name: str
    email: str
    company: str
    role: str
    segment: str

@app.post("/api/leads/new")
async def new_lead(lead: LeadInput, x_api_key: str = Header(None)):
    # Validação da sua chave de segurança
    if x_api_key != "sucesso@2029":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        # Usando o modelo atual recomendado pela API do Google
        model = genai.GenerativeModel("gemini-3.8-flash")
        
        prompt = f"""
        Você é um SDR experiente. Analise o seguinte lead e gere uma resposta personalizada de qualificação:
        - Nome: {lead.name}
        - E-mail: {lead.email}
        - Empresa: {lead.company}
        - Cargo: {lead.role}
        - Segmento: {lead.segment}
        """
        
        response = model.generate_content(prompt)
        return {"status": "success", "response": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a IA: {str(e)}")
