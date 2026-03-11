import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Configurações da Página
st.set_page_config(page_title="DeepRisk - Analisador", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco")
st.markdown("---")

# 2. Configuração do Gemini com Nomenclatura Forçada
if "GEMINI_API_KEY" not in st.secrets or st.secrets["GEMINI_API_KEY"] == "SUA_CHAVE_AQUI":
    st.error("⚠️ ERRO: Você não colocou sua chave real nos Secrets. Substitua 'SUA_CHAVE_AQUI' pela chave que começa com 'AIza'.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Mudança crucial: Usando o caminho completo 'models/...' para evitar o erro 404
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na configuração: {e}")
    st.stop()

# 3. Interface
uploaded_file = st.file_uploader("Suba sua planilha", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"Arquivo carregado!")

        if st.button("🚀 Iniciar Auditoria"):
            with st.spinner("Analisando..."):
                # Enviando apenas o necessário para não travar
                dados_texto = df.head(100).to_string()
                
                prompt = f"Analise estes dados de apostas e identifique padrões de fraude/arbitragem:\n\n{dados_texto}"
                
                # Chamada segura
                response = model.generate_content(prompt)
                
                st.markdown("### 📊 Relatório")
                st.info(response.text)
                
    except Exception as e:
        st.error(f"Erro: {e}")
