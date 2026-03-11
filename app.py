import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuração visual básica
st.set_page_config(page_title="DeepRisk - Auditoria", layout="wide")
st.title("🛡️ DeepRisk: Analisador de Risco")
st.markdown("---")

# 1. Configuração da IA (Direta e Simples)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
else:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Chamada purista do modelo
    model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Upload de Arquivo
uploaded_file = st.file_uploader("Suba sua planilha (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Lendo os dados
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"Arquivo carregado com {len(df)} linhas.")
        
        # Botão de ação
        if st.button("🚀 Iniciar Análise de IA"):
            with st.spinner("Analisando comportamentos suspeitos..."):
                # Enviamos apenas as primeiras 150 linhas para evitar erros de limite
                dados_texto = df.head(150).to_string()
                
                prompt = f"""
                Analise estes dados de apostas da EstrelaBet e identifique riscos de fraude ou arbitragem:
                
                {dados_texto}
                
                Destaque:
                - Apostas repetidas de 495,00 em ligas de baixa liquidez.
                - Stakes com centavos indicando Surebet.
                - Veredito final sobre o perfil do usuário.
                """
                
                # Execução da análise
                response = model.generate_content(prompt)
                
                st.markdown("### 📊 Relatório DeepRisk")
                st.write(response.text)
                
                st.download_button(
                    label="Baixar Relatório em TXT",
                    data=response.text,
                    file_name="auditoria_risco.txt",
                    mime="text/plain"
                )
                
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

st.markdown("---")
st.caption("DeepRisk v1.5 - Estabilidade Python 3.11")
