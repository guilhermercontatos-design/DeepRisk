import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Configurações Iniciais da Página
st.set_page_config(page_title="DeepRisk - Analisador", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco Avançada")
st.markdown("---")

# 2. Configuração do Gemini - USANDO A ROTA NOVA
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRO: Configure sua GEMINI_API_KEY nos Secrets.")
else:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Forçamos o modelo a carregar com a nomenclatura mais segura
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na configuração da IA: {e}")

# 3. Interface de Upload
uploaded_file = st.file_uploader("Suba sua planilha de apostas Altenar (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carregamento inteligente dos dados
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"Arquivo carregado com sucesso! {len(df)} linhas identificadas.")
        
        with st.expander("Clique para conferir os dados brutos"):
            st.dataframe(df.head(100))

        # 4. Botão de Auditoria
        if st.button("🚀 Iniciar Auditoria IA"):
            with st.spinner("O DeepRisk está processando os padrões de risco..."):
                try:
                    # Preparando dados (Primeiras 150 linhas para profundidade)
                    dados_audit = df.head(150).to_string()
                    
                    prompt = f"""
                    Você é um especialista em integridade de apostas esportivas da Altenar.
                    Analise os dados abaixo e identifique comportamentos profissionais ou fraudulentos:
                    
                    {dados_audit}
                    
                    Busque por:
                    1. Apostas repetidas de 495,00 (Tentativa de burlar limites).
                    2. Concentração anormal em ligas de baixa liquidez (Vietnã, Indonésia).
                    3. Uso de centavos quebrados (Surebet/Arbitragem).
                    
                    Dê um veredito final (Recreativo, Profissional ou Suspeito de Fraude). 
                    Responda em Português.
                    """
                    
                    # Chamada direta ao modelo corrigido
                    response = model.generate_content(prompt)
                    
                    st.markdown("### 📊 Relatório de Risco Gerado")
                    st.info(response.text)
                    
                    st.download_button(
                        label="📄 Baixar Relatório",
                        data=response.text,
                        file_name="relatorio_deeprisk.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    # Captura o erro específico para diagnóstico
                    st.error(f"Erro ao gerar conteúdo (Tente Reiniciar o App): {e}")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Aguardando upload para iniciar auditoria.")

st.markdown("---")
st.caption("DeepRisk v1.6 - Python 3.11 Compliance")
