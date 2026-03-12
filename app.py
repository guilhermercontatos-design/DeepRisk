import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import requests
import time

# ============================================
# FUNÇÃO PARA PROCESSAR CSV
# ============================================
def processar_csv(arquivo):
    """Processa CSV com formato da Altenar"""
    content = arquivo.read().decode('utf-8')
    lines = content.strip().split('\n')
    
    # Processar cabeçalho
    header_line = lines[0].strip()
    if header_line.startswith('"') and header_line.endswith('"'):
        header_line = header_line.strip('"')
    header = header_line.split(',')
    
    # Processar dados
    data = []
    for line in lines[1:]:
        if line.strip():
            clean_line = line.strip()
            if clean_line.startswith('"') and clean_line.endswith('"'):
                clean_line = clean_line.strip('"')
            values = clean_line.split(',')
            data.append(values)
    
    df = pd.DataFrame(data, columns=header)
    
    # Converter colunas numéricas
    for col in ['Bet prices', 'Total stake', 'Real win']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Converter datas
    for col in ['Created date', 'Bet event date', 'Settlement date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="DeepRisk",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ DeepRisk: Auditoria de Risco Avançada")
st.markdown("---")

# ============================================
# CONFIGURAÇÃO DAS APIS
# ============================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRO: Configure sua GEMINI_API_KEY nos Secrets.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Lista de modelos para tentar
    modelos_para_tentar = [
        'models/gemini-2.5-flash-lite',
        'models/gemini-2.5-flash',
        'models/gemini-2.0-flash',
    ]
    
    model = None
    modelo_escolhido = None
    
    for modelo_nome in modelos_para_tentar:
        try:
            model_test = genai.GenerativeModel(modelo_nome)
            test_response = model_test.generate_content(
                "teste",
                generation_config={"max_output_tokens": 1}
            )
            model = model_test
            modelo_escolhido = modelo_nome
            st.success(f"✅ Conectado: {modelo_nome}")
            break
        except Exception as e:
            if "429" in str(e):
                st.warning(f"⚠️ {modelo_nome} sem cota")
            continue
    
    if model is None:
        st.error("❌ NENHUM MODELO DISPONÍVEL NO MOMENTO")
        st.stop()
    
    ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"
    
    # Sidebar com informações
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1E1E2E/9D9DFF?text=DeepRisk", use_column_width=True)
        st.markdown("### ⚙️ Configurações")
        validar_api = st.checkbox("🔍 Validar com The Odds API", value=True)
        st.markdown("---")
        st.markdown(f"**Modelo ativo:** {modelo_escolhido}")
        st.markdown("**Status:** 🟢 Online")
    
except Exception as e:
    st.error(f"Erro: {e}")
    st.stop()

# ============================================
# INTERFACE PRINCIPAL
# ============================================
uploaded_file = st.file_uploader(
    "Suba sua planilha de apostas Altenar (CSV ou Excel)",
    type=['csv', 'xlsx']
)

if uploaded_file is not None:
    try:
        # Carregar dados
        if uploaded_file.name.endswith('.csv'):
            df = processar_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado! {len(df)} linhas identificadas.")
        
        # Identificar jogador
        if 'Player name' in df.columns:
            jogador = df['Player name'].iloc[0]
            st.subheader(f"📊 Analisando jogador: **{jogador}**")
        
        with st.expander("👁️ Visualizar dados brutos"):
            st.dataframe(df.head(10))
        
        # Métricas básicas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Apostas", len(df))
        with col2:
            if 'Total stake' in df.columns:
                st.metric("Total Apostado", f"R$ {df['Total stake'].sum():,.2f}")
        with col3:
            if 'Bet status' in df.columns:
                ganhas = len(df[df['Bet status'] == 'Ganha'])
                st.metric("Taxa Acerto", f"{(ganhas/len(df)*100):.1f}%")
        
        # Botão de análise
        if st.button("🚀 INICIAR AUDITORIA IA", type="primary", use_container_width=True):
            with st.spinner("O DeepRisk está processando os padrões de risco..."):
                
                # Preparar dados para IA
                dados_audit = df.head(50).to_string()
                
                prompt = f"""
Você é um especialista em integridade de apostas esportivas da Altenar.
Analise os dados abaixo e identifique comportamentos profissionais ou fraudulentos:

{dados_audit}

Busque por:
1. Apostas repetidas de 495,00 (Tentativa de burlar limites).
2. Concentração anormal em ligas de baixa liquidez (Vietnã, Indonésia).
3. Uso de centavos quebrados (Surebet/Arbitragem).
4. Apostas de última hora (late odds).
5. Taxa de acerto anormal (>60%).

Dê um veredito final (Recreativo, Profissional ou Suspeito de Fraude).
Responda em Português, seja detalhado.
"""
                
                # Chamar IA
                response = model.generate_content(prompt)
                
                st.markdown("### 📊 Relatório de Risco Gerado")
                st.info(response.text)
                
                # Botão de download
                st.download_button(
                    label="📄 Baixar Relatório",
                    data=response.text,
                    file_name=f"deeprisk_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                )
                
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.exception(e)
else:
    st.info("Aguardando upload para iniciar auditoria.")

st.markdown("---")
st.caption(f"DeepRisk v3.0 - Modelo: {modelo_escolhido if 'modelo_escolhido' in locals() else 'N/A'}")
