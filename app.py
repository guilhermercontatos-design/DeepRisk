import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Configurações Iniciais da Página
st.set_page_config(page_title="DeepRisk - Analisador", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco Avançada")
st.markdown("---")

# 2. Configuração do Gemini
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRO: Configure sua GEMINI_API_KEY nos Secrets.")
else:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # SOLUÇÃO 1: Verificar modelos disponíveis e usar um alternativo
        # Lista os modelos disponíveis para debug (opcional)
        with st.expander("Modelos disponíveis (debug)", expanded=False):
            try:
                models = genai.list_models()
                for m in models:
                    if 'generateContent' in m.supported_generation_methods:
                        st.write(f"- {m.name}")
            except:
                st.write("Não foi possível listar modelos")
        
        # SOLUÇÃO 2: Usar um modelo diferente ou verificar a nomenclatura correta
        # Tente um destes modelos:
        # - 'gemini-1.5-flash' (pode precisar ser 'models/gemini-1.5-flash')
        # - 'gemini-pro' (modelo mais estável e amplamente disponível)
        # - 'gemini-1.0-pro' (versão anterior)
        
        try:
            # Tenta primeiro com gemini-pro (mais estável)
            model = genai.GenerativeModel(model_name='gemini-pro')
        except:
            # Se falhar, tenta com o caminho completo
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            
    except Exception as e:
        st.error(f"Erro na configuração da IA: {e}")
        st.stop()

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
                    # Preparando dados (Primeiras 50 linhas para evitar excesso de tokens)
                    dados_audit = df.head(50).to_string()
                    
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
                    st.error(f"Erro ao gerar conteúdo: {e}")
                    
                    # SOLUÇÃO 3: Debug mais detalhado
                    st.error("Detalhes do erro:")
                    st.code(str(e))
                    
                    # Sugestão de solução
                    st.warning("""
                    **Sugestões:**
                    1. Verifique se sua API key tem acesso ao Gemini 1.5 Flash
                    2. Tente usar 'gemini-pro' como modelo (já configurado no código)
                    3. Verifique se você ativou a API correta no Google Cloud Console
                    4. Acesse https://makersuite.google.com/app/apikey para verificar sua chave
                    """)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Aguardando upload para iniciar auditoria.")

st.markdown("---")
st.caption("DeepRisk v1.6 - Python 3.11 Compliance")
