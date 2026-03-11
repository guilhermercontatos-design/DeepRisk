import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# 1. Configuração da Página
st.set_page_config(page_title="DeepRisk - Analisador de Risco", layout="wide")
st.title("🛡️ DeepRisk: Analisador de Risco Avançado")
st.subheader("Focado em Padrões de Arbitragem e Fraude - EstrelaBet")
st.markdown("---")

# 2. Configuração do Gemini - Versão Estável
def inicializar_modelo():
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("ERRO: Chave 'GEMINI_API_KEY' não encontrada nos Secrets.")
            return None
        
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Mudança importante: Usando a string direta que a API atual exige
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"Erro ao configurar IA: {e}")
        return None

model = inicializar_modelo()

# 3. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste o relatório de apostas aqui", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Leitura automática
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("Arquivo carregado com sucesso!")
        
        with st.expander("Ver dados brutos"):
            st.dataframe(df)

        # 4. Botão de Análise
        if st.button("🚀 Iniciar Análise com IA"):
            if model is None:
                st.error("O modelo não foi inicializado. Verifique sua chave API.")
            else:
                with st.spinner("Analisando padrões de apostas..."):
                    # Pegamos as primeiras 150 linhas para uma análise profunda
                    dados_para_ia = df.head(150).to_string()
                    
                    prompt = f"""
                    Analise os seguintes dados de apostas e identifique comportamentos profissionais ou fraudulentos:
                    
                    {dados_para_ia}
                    
                    Procure por:
                    - Apostas repetidas com stakes fixas (ex: 495.00) em ligas pequenas.
                    - Padrões de Arbitragem (stakes com valores estranhos/quebrados).
                    - Concentração excessiva em mercados específicos (Vietnã, Indonésia).
                    
                    Dê um veredito final sobre o nível de risco deste jogador. Responda em Português.
                    """
                    
                    # Chamada direta
                    response = model.generate_content(prompt)
                    
                    st.markdown("### 📊 Relatório de Auditoria")
                    st.write(response.text)
                    
                    st.download_button(
                        label="Baixar Relatório",
                        data=response.text,
                        file_name="analise_deeprisk.txt",
                        mime="text/plain"
                    )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando upload do arquivo para análise.")

st.markdown("---")
st.caption("DeepRisk v1.2 - Powered by Gemini 1.5 Flash")
