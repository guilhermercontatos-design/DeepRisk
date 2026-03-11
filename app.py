import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="DeepRisk - Validação", layout="wide")

ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"

def buscar_odds_simples(esporte="soccer_epl"):
    url = f"https://api.the-odds-api.com/v4/sports/{esporte}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

st.title("🛡️ DeepRisk - Validação de Odds")

# Upload
uploaded_file = st.file_uploader("Suba sua planilha", type=['csv', 'xlsx'])

if uploaded_file:
    # Carregar dados
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.success(f"✅ {len(df)} linhas carregadas")
    st.dataframe(df.head())
    
    # Botão para validar
    if st.button("🔍 Validar Odds com API"):
        with st.spinner("Buscando odds..."):
            odds = buscar_odds_simples("soccer_epl")
            
            if odds:
                st.success(f"✅ {len(odds)} eventos encontrados!")
                
                # Criar DataFrame dos eventos
                eventos = []
                for jogo in odds[:5]:  # Mostrar só 5
                    for bookmaker in jogo.get('bookmakers', [])[:2]:  # Só 2 bookmakers
                        for market in bookmaker.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                eventos.append({
                                    'Jogo': f"{jogo['home_team']} vs {jogo['away_team']}",
                                    'Casa': bookmaker['title'],
                                    'Mercado': outcome['name'],
                                    'Odds': outcome['price']
                                })
                
                if eventos:
                    st.dataframe(pd.DataFrame(eventos))
            else:
                st.error("Não foi possível buscar odds")
