import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import requests
import time

# 1. Configurações da Página
st.set_page_config(page_title="DeepRisk - Validação Odds", layout="wide")
st.title("🛡️ DeepRisk: Validação de Odds em Tempo Real")
st.markdown("---")

# 2. Configuração das APIs
try:
    # GEMINI
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ Configure sua GEMINI_API_KEY nos Secrets!")
        st.stop()
    
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    
    # ODDS API - SUA CHAVE AQUI
    ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"
    ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
    
    # Teste rápido da API
    st.success("✅ APIs configuradas!")
    
    # Mostrar saldo da API (requisições restantes)
    st.info(f"🔑 API Key configurada: {ODDS_API_KEY[:5]}...{ODDS_API_KEY[-5:]}")
    
except Exception as e:
    st.error(f"Erro na configuração: {e}")
    st.stop()

# 3. Funções da The Odds API
@st.cache_data(ttl=3600)
def testar_conexao():
    """Testa se a API está funcionando"""
    url = f"{ODDS_BASE_URL}/sports"
    params = {"apiKey": ODDS_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Erro {response.status_code}"
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=300)
def buscar_odds_ao_vivo(esporte="soccer_brazil_campeonato"):
    """Busca odds ao vivo de um esporte"""
    url = f"{ODDS_BASE_URL}/sports/{esporte}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us,uk,au,eu,br",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Headers mostram quantas requisições restam
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            used = response.headers.get('x-requests-used', 'N/A')
            return response.json(), remaining, used
        else:
            return None, None, None
    except Exception as e:
        st.error(f"Erro na busca: {e}")
        return None, None, None

# 4. Interface Principal
st.markdown("### 🌐 Teste de Conexão com The Odds API")

# Botão para testar
if st.button("🔍 Testar Conexão com API"):
    with st.spinner("Testando conexão..."):
        sucesso, resultado = testar_conexao()
        
        if sucesso:
            st.success("✅ Conexão bem sucedida!")
            st.write(f"📊 Esportes disponíveis: {len(resultado)}")
            
            # Mostrar alguns esportes
            st.dataframe(pd.DataFrame(resultado[:5]))
        else:
            st.error(f"❌ Falha na conexão: {resultado}")

# 5. Upload da planilha
uploaded_file = st.file_uploader("Suba sua planilha de apostas", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carregar dados
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado! {len(df)} linhas")
        
        with st.expander("👁️ Visualizar dados"):
            st.dataframe(df.head(10))
        
        # 6. Seletor de análise
        if st.checkbox("🌐 Validar odds com The Odds API"):
            st.markdown("### 🔍 Validação em Tempo Real")
            
            # Mapear ligas
            ligas_mapeadas = {
                'Brasileirão': 'soccer_brazil_campeonato',
                'Premier League': 'soccer_epl',
                'La Liga': 'soccer_spain_la_liga',
                'Serie A': 'soccer_italy_serie_a',
                'Bundesliga': 'soccer_germany_bundesliga',
                'NBA': 'basketball_nba'
            }
            
            # Identificar ligas únicas na planilha
            ligas_na_planilha = df['Bet champs'].unique() if 'Bet champs' in df.columns else []
            
            st.write("**Ligas encontradas na planilha:**")
            for liga in ligas_na_planilha:
                if liga in ligas_mapeadas:
                    st.write(f"✅ {liga} → {ligas_mapeadas[liga]}")
                else:
                    st.write(f"⚠️ {liga} → Sem mapeamento")
            
            # Botão para buscar odds
            if st.button("🚀 Buscar Odds do Mercado"):
                esporte_selecionado = st.selectbox(
                    "Escolha um esporte para buscar odds",
                    list(ligas_mapeadas.values()) + ["soccer_brazil_campeonato"]
                )
                
                with st.spinner("Buscando odds ao vivo..."):
                    odds, remaining, used = buscar_odds_ao_vivo(esporte_selecionado)
                    
                    if odds:
                        st.success(f"✅ Odds encontradas! Requisições restantes: {remaining}")
                        
                        # Mostrar odds encontradas
                        df_odds = pd.DataFrame(odds)
                        st.dataframe(df_odds[['home_team', 'away_team', 'commence_time']])
                        
                        # Comparar com apostas da planilha
                        st.markdown("#### 📊 Comparação com suas apostas")
                        
                        comparacoes = []
                        for _, aposta in df.head(10).iterrows():
                            for jogo in odds[:5]:  # Comparar com primeiros jogos
                                if aposta['Bet events'].find(jogo['home_team']) >= 0 or aposta['Bet events'].find(jogo['away_team']) >= 0:
                                    comparacoes.append({
                                        'Aposta ID': aposta['Bet id'],
                                        'Evento': aposta['Bet events'],
                                        'Odds Apostada': aposta['Bet prices'],
                                        'Odds Mercado': jogo.get('bookmakers', [{}])[0].get('markets', [{}])[0].get('outcomes', [{}])[0].get('price', 'N/A'),
                                        'Status': '🔍 Encontrado'
                                    })
                        
                        if comparacoes:
                            st.dataframe(pd.DataFrame(comparacoes))
                        else:
                            st.info("Nenhuma correspondência encontrada com odds ao vivo")
                    else:
                        st.error("Não foi possível buscar odds")
        
        # 7. Botão de auditoria normal
        if st.button("📊 Iniciar Auditoria Padrão"):
            with st.spinner("Analisando..."):
                # Análise simples
                st.markdown("### 📊 Resultados da Análise")
                
                # Detectar padrões suspeitos
                suspeitos = []
                
                if 'Total stake' in df.columns:
                    apostas_495 = df[df['Total stake'] == 495.00]
                    if len(apostas_495) > 0:
                        suspeitos.append(f"🔴 {len(apostas_495)} apostas com valor R$ 495,00")
                
                if 'Bet champs' in df.columns:
                    ligas_suspeitas = ['Vietnam', 'Indonésia', 'Mianmar', 'Camboja']
                    for liga in ligas_suspeitas:
                        count = len(df[df['Bet champs'].str.contains(liga, case=False, na=False)])
                        if count > 0:
                            suspeitos.append(f"🟡 {count} apostas em liga suspeita: {liga}")
                
                if suspeitos:
                    for s in suspeitos:
                        st.warning(s)
                else:
                    st.success("Nenhum padrão suspeito detectado")
                    
    except Exception as e:
        st.error(f"Erro: {e}")

st.markdown("---")
st.caption("DeepRisk v2.5 - API Key: " + ODDS_API_KEY[:5] + "..." + ODDS_API_KEY[-5:])
