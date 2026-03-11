import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="DeepRisk - Odds Brasil", layout="wide")
st.title("🇧🇷 DeepRisk - Validação de Odds - Futebol Brasileiro")

# SUA CHAVE
ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"

def buscar_odds_brasil():
    """Busca odds de futebol brasileiro"""
    
    # Lista de ligas brasileiras na The Odds API
    ligas_brasileiras = [
        "soccer_brazil_campeonato",  # Brasileirão Série A
        "soccer_brazil_cup",          # Copa do Brasil
        "soccer_brazil_serie_b"       # Série B (se disponível)
    ]
    
    resultados = []
    
    for liga in ligas_brasileiras:
        url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "br,us,eu",  # Inclui região Brasil
            "markets": "h2h",        # Resultado final
            "oddsFormat": "decimal"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                odds = response.json()
                if odds:  # Se encontrou jogos
                    resultados.extend(odds)
                    st.success(f"✅ {liga}: {len(odds)} jogos encontrados!")
            else:
                st.warning(f"⚠️ {liga}: Sem jogos no momento")
                
        except Exception as e:
            st.error(f"Erro na liga {liga}: {e}")
    
    return resultados

def listar_todas_ligas_disponiveis():
    """Lista todas as ligas disponíveis na API"""
    url = "https://api.the-odds-api.com/v4/sports"
    params = {"apiKey": ODDS_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            sports = response.json()
            
            # Filtrar apenas ligas de futebol
            ligas_futebol = [s for s in sports if 'soccer' in s['key']]
            
            # Mostrar ligas brasileiras primeiro
            st.markdown("### ⚽ Ligas de Futebol Disponíveis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🇧🇷 Ligas Brasileiras:**")
                for liga in ligas_futebol:
                    if 'brazil' in liga['key']:
                        st.write(f"✅ `{liga['key']}` - {liga['title']}")
            
            with col2:
                st.markdown("**🌍 Outras Ligas:**")
                outras = [l for l in ligas_futebol if 'brazil' not in l['key']][:10]
                for liga in outras:
                    st.write(f"📌 `{liga['key']}` - {liga['title']}")
            
            return ligas_futebol
    except Exception as e:
        st.error(f"Erro ao listar ligas: {e}")
        return []

# INTERFACE PRINCIPAL
st.markdown("---")

# Primeiro, mostrar todas as ligas disponíveis
with st.expander("📋 Ver todas as ligas disponíveis", expanded=False):
    listar_todas_ligas_disponiveis()

# Botão para buscar jogos do Brasil
if st.button("🇧🇷 Buscar Jogos do Brasil AGORA", type="primary"):
    with st.spinner("Buscando odds de futebol brasileiro..."):
        jogos_brasil = buscar_odds_brasil()
        
        if jogos_brasil:
            st.success(f"🎉 Encontrados {len(jogos_brasil)} jogos brasileiros!")
            
            # Processar e mostrar os jogos
            dados_jogos = []
            for jogo in jogos_brasil:
                for bookmaker in jogo.get('bookmakers', [])[:3]:  # Top 3 casas
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            dados_jogos.append({
                                'Jogo': f"{jogo['home_team']} vs {jogo['away_team']}",
                                'Data': datetime.fromisoformat(jogo['commence_time'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M'),
                                'Casa': bookmaker['title'],
                                'Mercado': outcome['name'],
                                'Odds': outcome['price']
                            })
            
            if dados_jogos:
                df_jogos = pd.DataFrame(dados_jogos)
                st.dataframe(df_jogos, use_container_width=True)
                
                # Estatísticas
                st.info(f"📊 Total de odds encontradas: {len(dados_jogos)}")
            else:
                st.warning("Jogos encontrados mas sem odds disponíveis")
        else:
            st.warning("""
            ⚠️ **Nenhum jogo brasileiro no momento**
            
            Motivos possíveis:
            - Não há jogos AO VIVO agora
            - A liga pode estar entre temporadas
            - Teste com campeonatos europeus que estão em andamento
            
            **Sugestão:** Use a opção abaixo para ver jogos europeus (sempre têm!)
            """)

# Opção para ver jogos europeus (garantido)
st.markdown("---")
st.markdown("### 🌍 Ver jogos europeus (sempre disponíveis)")

if st.button("🇪🇺 Buscar Premier League"):
    with st.spinner("Buscando Premier League..."):
        url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "eu,uk",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            jogos = response.json()
            st.success(f"✅ {len(jogos)} jogos da Premier League encontrados!")
            
            dados = []
            for jogo in jogos[:5]:  # Mostrar só 5
                for bookmaker in jogo.get('bookmakers', [])[:2]:
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            dados.append({
                                'Jogo': f"{jogo['home_team']} vs {jogo['away_team']}",
                                'Casa': bookmaker['title'],
                                'Mercado': outcome['name'],
                                'Odds': outcome['price']
                            })
            
            st.dataframe(pd.DataFrame(dados))

# Upload da sua planilha
st.markdown("---")
st.markdown("### 📤 Validar suas apostas")

uploaded_file = st.file_uploader("Suba sua planilha de apostas", type=['csv', 'xlsx'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.success(f"✅ {len(df)} apostas carregadas")
    st.dataframe(df.head())
    
    # Mostrar ligas na sua planilha
    if 'Bet champs' in df.columns:
        st.markdown("**Ligas nas suas apostas:**")
        ligas_unicas = df['Bet champs'].unique()
        for liga in ligas_unicas:
            st.write(f"- {liga}")
