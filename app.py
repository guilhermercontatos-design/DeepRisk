import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="DeepRisk - Diagnóstico", layout="wide")
st.title("🔧 Diagnóstico da API Gemini")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Configure sua GEMINI_API_KEY nos Secrets")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    st.subheader("📋 Modelos Disponíveis:")
    
    # Listar todos os modelos
    models = genai.list_models()
    
    modelos_disponiveis = []
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            modelos_disponiveis.append(m.name)
            st.write(f"✅ `{m.name}` - Suporta generateContent")
        else:
            st.write(f"❌ `{m.name}` - Não suporta generateContent")
    
    st.subheader("🎯 Modelos Recomendados:")
    for modelo in modelos_disponiveis:
        if 'pro' in modelo.lower():
            st.success(f"👉 Tente usar: `{modelo}`")
            
except Exception as e:
    st.error(f"Erro: {e}")
