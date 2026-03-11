import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# 1. Configuração da Página
st.set_page_config(page_title="DeepRisk - Analisador de Risco", layout="wide")
st.title("🛡️ DeepRisk: Analisador de Risco Avançado")
st.subheader("Focado em Padrões de Arbitragem e Fraude - EstrelaBet")
st.markdown("---")

# 2. Configuração do Gemini com tratamento de erro completo
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("ERRO: Chave 'GEMINI_API_KEY' não encontrada nos Secrets do Streamlit.")
    else:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # Usando o nome do modelo corrigido para evitar o erro 404
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na inicialização do modelo: {e}")

# 3. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste o relatório de apostas aqui", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Leitura automática (CSV ou Excel)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("Arquivo carregado com sucesso!")
        
        with st.expander("Ver dados brutos"):
            st.dataframe(df)

        # 4. Botão de Análise
        if st.button("🚀 Iniciar Análise com IA"):
            with st.spinner("Analisando padrões de apostas..."):
                
                # Selecionamos colunas estratégicas se existirem, senão usamos o que tiver
                # Adaptado para as colunas da sua imagem (Bet champs, Total stake, etc)
                colunas_disponiveis = df.columns.tolist()
                dados_para_ia = df.head(100).to_string() # Analisa as primeiras 100 linhas
                
                prompt = f"""
                Você é um especialista em monitoramento de integridade e risco em apostas esportivas.
                Analise estes dados de apostas da EstrelaBet/Altenar e identifique padrões suspeitos:
                
                {dados_para_ia}
                
                Considere:
                1. Apostas repetidas com valores idênticos (ex: 495.00) em ligas de baixa liquidez (Vietnã, Indonésia).
                2. Horários de aposta muito próximos para o mesmo evento.
                3. Valores de stake quebrados (centavos) que indicam uso de calculadoras de arbitragem.
                4. Conclusão: Este perfil apresenta risco de fraude ou profissionalismo?
                
                Responda em Português de forma estruturada.
                """
                
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
st.caption("DeepRisk v1.1 - Modelo Gemini 1.5 Flash")
