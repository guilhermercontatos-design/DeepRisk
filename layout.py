# diagnostico.py - Diagnóstico completo da API Gemini
import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

st.set_page_config(page_title="🔧 Diagnóstico DeepRisk", layout="wide")
st.title("🔧 Diagnóstico da API Gemini")
st.markdown("---")

# Verificar se a chave existe
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY não encontrada nos Secrets!")
    st.stop()
else:
    st.success("✅ GEMINI_API_KEY encontrada nos Secrets")

# Mostrar a chave (parcialmente)
chave = st.secrets["GEMINI_API_KEY"]
st.info(f"🔑 Chave: {chave[:5]}...{chave[-5:]}")

st.markdown("---")

# 1. TESTE DE CONEXÃO BÁSICA
st.subheader("1. Teste de Conexão Básica")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.success("✅ genai.configure() executado com sucesso")
except Exception as e:
    st.error(f"❌ Erro no configure: {e}")

st.markdown("---")

# 2. LISTAR MODELOS DISPONÍVEIS
st.subheader("2. Modelos Disponíveis")

try:
    models = genai.list_models()
    
    st.write(f"**Total de modelos encontrados:** {len(models)}")
    
    modelos_com_generate = []
    modelos_sem_generate = []
    
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            modelos_com_generate.append(m.name)
        else:
            modelos_sem_generate.append(m.name)
    
    st.success(f"✅ {len(modelos_com_generate)} modelos suportam generateContent")
    
    if modelos_com_generate:
        st.write("**Modelos disponíveis para uso:**")
        for modelo in modelos_com_generate:
            st.write(f"- `{modelo}`")
    else:
        st.error("❌ Nenhum modelo com generateContent encontrado!")
    
    st.write(f"**Modelos sem generateContent:** {len(modelos_sem_generate)}")
    
except Exception as e:
    st.error(f"❌ Erro ao listar modelos: {e}")

st.markdown("---")

# 3. TESTAR CADA MODELO INDIVIDUALMENTE
st.subheader("3. Teste Individual de Modelos")

if modelos_com_generate:
    for modelo_nome in modelos_com_generate[:5]:  # Testar só os primeiros 5
        with st.expander(f"Testando: {modelo_nome}"):
            try:
                model = genai.GenerativeModel(modelo_nome)
                st.write("✅ Modelo criado")
                
                # Teste mínimo
                response = model.generate_content(
                    "Responda apenas 'OK'",
                    generation_config={
                        "max_output_tokens": 5,
                        "temperature": 0.1
                    }
                )
                st.success(f"✅ Resposta: {response.text}")
                
            except Exception as e:
                st.error(f"❌ Erro: {e}")
                
                # Análise do erro
                erro_str = str(e)
                if "429" in erro_str:
                    st.warning("⚠️ Erro 429: Cota excedida!")
                elif "404" in erro_str:
                    st.warning("⚠️ Erro 404: Modelo não encontrado")
                elif "403" in erro_str:
                    st.warning("⚠️ Erro 403: Permissão negada")
else:
    st.error("❌ Não há modelos para testar")

st.markdown("---")

# 4. VERIFICAR COTAS (se possível)
st.subheader("4. Informações de Cota")

try:
    # Tentar fazer uma requisição para ver headers
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {"x-goog-api-key": st.secrets["GEMINI_API_KEY"]}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        st.success("✅ API respondendo normalmente")
        
        # Verificar headers de cota (se existirem)
        remaining = response.headers.get('x-ratelimit-remaining', 'N/A')
        limit = response.headers.get('x-ratelimit-limit', 'N/A')
        
        st.info(f"📊 Cotas - Restantes: {remaining} | Limite: {limit}")
    else:
        st.error(f"❌ API retornou status {response.status_code}")
        st.code(response.text)
        
except Exception as e:
    st.error(f"❌ Erro na verificação de cotas: {e}")

st.markdown("---")

# 5. HORA DO SISTEMA
st.subheader("5. Informações de Tempo")

from datetime import datetime
import pytz

# Horário atual
agora = datetime.now()
st.write(f"🕐 Hora local: {agora.strftime('%H:%M:%S')}")
st.write(f"📅 Data local: {agora.strftime('%d/%m/%Y')}")

# Horário do Pacífico (onde a cota reseta)
pacifico = pytz.timezone('US/Pacific')
hora_pacifico = datetime.now(pacifico)
st.write(f"🌎 Horário do Pacífico: {hora_pacifico.strftime('%H:%M:%S')}")

# Verificar se é horário de reset
if hora_pacifico.hour == 0 and hora_pacifico.minute < 10:
    st.success("✅ Horário de reset (meia-noite no Pacífico)")
else:
    st.info(f"⏳ Reset acontece à meia-noite do Pacífico (faltam {24 - hora_pacifico.hour}h)")

st.markdown("---")

# 6. RECOMENDAÇÕES
st.subheader("6. Recomendações")

if modelos_com_generate:
    st.success("✅ Há modelos disponíveis! O problema pode ser no seu código.")
    st.markdown("""
    **Sugestões:**
    1. Use um dos modelos listados acima no seu `app.py`
    2. Verifique se o modelo está sendo chamado corretamente
    3. Adicione tratamento de erros mais robusto
    """)
else:
    st.error("❌ Nenhum modelo disponível!")
    st.markdown("""
    **Soluções:**
    1. ⏰ Aguarde até depois das 16h (horário de Brasília)
    2. 💳 Configure faturamento no Google Cloud
    3. 🔑 Gere uma nova API key no [Google AI Studio](https://aistudio.google.com)
    4. 📧 Entre em contato com suporte do Google
    """)

st.markdown("---")
st.caption(f"Diagnóstico realizado em: {agora.strftime('%d/%m/%Y %H:%M:%S')}")
