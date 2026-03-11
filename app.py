import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# 1. Configuração da Página e Estilo
st.set_page_config(page_title="DeepRisk - Altenar Audit", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco Altenar")
st.markdown("---")

# 2. Configuração do Gemini
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Usando a versão estável mais recente
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro de configuração: Verifique se a 'GEMINI_API_KEY' está nos Secrets. Detalhe: {e}")

# 3. Upload do Arquivo
uploaded_file = st.file_uploader("Suba o arquivo CSV extraído da Altenar", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Leitura dos dados
    try:
        if uploaded_file.name.endswith('.csv'):
            # Tenta ler com vírgula ou ponto e vírgula
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"Arquivo carregado: {len(df)} apostas encontradas.")
        
        # Exibe os dados para conferência
        with st.expander("Visualizar dados brutos"):
            st.dataframe(df.head(10))

        # 4. Botão de Análise
        if st.button("🚀 Iniciar Análise de Risco com IA"):
            with st.spinner("O Gemini está analisando os padrões de aposta..."):
                
                # Preparando o resumo para a IA não estourar o limite de tokens
                # Focamos nas colunas que você mostrou na foto
                resumo_dados = df[['Bet champs', 'Bet events', 'Total stake', 'Bet prices', 'Created date']].to_string()
                
                prompt = f"""
                Você é um analista de risco sênior de uma casa de apostas. 
                Analise os seguintes dados de apostas da plataforma Altenar:
                
                {resumo_dados}
                
                Identifique especificamente:
                1. Tentativas de burlar limites (apostas repetidas de valores altos como 495,00 ou próximos ao limite).
                2. Sinais de Arbitragem/Surebet (valores de stake quebrados com centavos precisos).
                3. Risco por liga (Ex: Alto volume em ligas de baixa liquidez como Indonésia Liga 3 ou Vietnã).
                4. Veredito final: O jogador é recreativo, profissional ou fraudador?
                
                Responda em português, de forma clara e profissional.
                """
                
                # Chamada para o modelo
                response = model.generate_content(prompt)
                
                # 5. Exibição do Relatório
                st.markdown("### 📊 Relatório de Auditoria DeepRisk")
                st.write(response.text)
                
                # Download do Relatório
                st.download_button(
                    label="Baixar Relatório em TXT",
                    data=response.text,
                    file_name="relatorio_risco_gemini.txt",
                    mime="text/plain"
                )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Aguardando upload do arquivo para análise.")

st.markdown("---")
st.caption("DeepRisk v1.0 - Powered by Gemini 1.5 Flash")
