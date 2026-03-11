import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Configurações da Página
st.set_page_config(page_title="DeepRisk - Analisador", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco Avançada")
st.markdown("---")

# 2. Configuração do Gemini
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Configure sua GEMINI_API_KEY nos Secrets do Streamlit!")
    st.info("""
    **Como configurar:**
    1. Vá para o painel do Streamlit Cloud
    2. Acesse as configurações do app
    3. Adicione GEMINI_API_KEY nos Secrets
    """)
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # TENTATIVA 1: Caminho completo (mais provável de funcionar)
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except:
        # TENTATIVA 2: Modelo alternativo se o primeiro falhar
        model = genai.GenerativeModel('gemini-pro')
        
except Exception as e:
    st.error(f"Erro na configuração da IA: {e}")
    st.stop()

# 3. Interface
uploaded_file = st.file_uploader("Suba sua planilha de apostas Altenar", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carregamento inteligente
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado! {len(df)} linhas identificadas.")
        
        with st.expander("👁️ Visualizar dados"):
            st.dataframe(df.head(10))

        if st.button("🚀 Iniciar Auditoria IA"):
            with st.spinner("DeepRisk analisando padrões de risco..."):
                try:
                    # Preparando dados para análise
                    dados_analise = df.head(100).to_string()
                    
                    prompt = f"""
                    Você é um especialista em integridade de apostas esportivas.
                    Analise os dados abaixo e identifique:

                    1. Apostas repetidas de valores próximos a 495,00
                    2. Concentração em ligas de baixa liquidez (Vietnã, Indonésia)
                    3. Uso de centavos quebrados (padrões de arbitragem)

                    DADOS:
                    {dados_analise}

                    Forneça um relatório conciso em português com:
                    - Padrões suspeitos encontrados
                    - Classificação de risco (Recreativo / Profissional / Suspeito)
                    - Recomendações
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.markdown("### 📊 Relatório de Risco")
                    st.info(response.text)
                    
                    # Botão para download
                    st.download_button(
                        label="📥 Baixar Relatório",
                        data=response.text,
                        file_name="relatorio_deeprisk.txt"
                    )
                    
                except Exception as e:
                    st.error(f"Erro na geração: {e}")
                    
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
else:
    st.info("📤 Aguardando upload do arquivo...")

st.markdown("---")
st.caption("DeepRisk v1.6 - Python 3.11")
