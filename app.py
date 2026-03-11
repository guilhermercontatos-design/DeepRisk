import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="DeepRisk - EstrelaBet Analyst", layout="wide")

# Conectando com a sua chave que você salvou nos Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Erro: A chave GEMINI_API_KEY não foi encontrada nos Secrets do Streamlit.")

st.title("🛡️ DeepRisk: Analisador de Risco Avançado")
st.subheader("Focado em Padrões de Arbitragem e Fraude - EstrelaBet")

# Upload do arquivo da Altenar (CSV ou Excel)
uploaded_file = st.file_uploader("Arraste o relatório de apostas aqui", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carregando os dados
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("Arquivo carregado com sucesso!")
        
        # Mostrar prévia dos dados
        with st.expander("Ver dados brutos"):
            st.write(df.head())

        # Botão para iniciar análise
        if st.button("🚀 Iniciar Análise com IA"):
            with st.spinner("O Gemini está analisando os padrões de risco..."):
                
                # Transformando os dados em texto para a IA ler (resumo)
                resumo_dados = df.describe().to_string()
                colunas = ", ".join(df.columns)
                
                prompt = f"""
                Você é um analista de risco sênior especializado em casas de apostas que utilizam a plataforma Altenar.
                Analise os seguintes dados de apostas e identifique:
                1. Padrões de Arbitragem (Surebet).
                2. Comportamento suspeito de contas (valores fora do comum).
                3. Probabilidade de fraude em escala de 0 a 100%.
                
                Colunas disponíveis: {colunas}
                Resumo estatístico:
                {resumo_dados}
                
                Dê um veredito final claro para a gerência da EstrelaBet.
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.header("📋 Relatório do Analista IA")
                st.write(response.text)
                
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Aguardando upload do arquivo para análise.")
