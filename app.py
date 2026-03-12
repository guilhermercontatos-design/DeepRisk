import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import requests
import time

# ⚡ IMPORTAR O LAYOUT PROFISSIONAL (apenas UMA vez)
from layout import *

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================

# Aplicar tema profissional
aplicar_tema_profissional()

# Título principal com estilo
titulo_principal()

# ============================================
# CONFIGURAÇÃO DAS APIS
# ============================================

if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERROR: Configure sua GEMINI_API_KEY nos Secrets.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # LISTA DE MODELOS PARA TENTAR (do mais leve ao mais pesado)
    modelos_para_tentar = [
        'models/gemini-2.5-flash-lite',  # 1.000 req/dia
        'models/gemini-2.5-flash',       # 250 req/dia
        'models/gemini-2.0-flash',       # Legacy
        'models/gemini-2.0-flash-lite',  # Legacy leve
    ]
    
    model = None
    modelo_escolhido = None
    erros_encontrados = []
    
    # Barra de progresso para tentativas
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, modelo_nome in enumerate(modelos_para_tentar):
        progress_bar.progress((idx + 1) / len(modelos_para_tentar))
        status_text.text(f"🔄 Tentando conectar com: {modelo_nome}")
        
        try:
            # Tentar criar o modelo
            model_test = genai.GenerativeModel(modelo_nome)
            
            # Teste mínimo para verificar se funciona
            test_response = model_test.generate_content(
                "teste",
                generation_config={
                    "max_output_tokens": 1,
                    "temperature": 0.1
                }
            )
            
            # Se chegou aqui, funcionou!
            model = model_test
            modelo_escolhido = modelo_nome
            status_text.text(f"✅ Conectado com sucesso: {modelo_nome}")
            break
            
        except Exception as e:
            erro_msg = str(e)
            erros_encontrados.append(f"{modelo_nome}: {erro_msg[:100]}...")
            
            if "429" in erro_msg:
                status_text.text(f"⚠️ {modelo_nome} sem cota no momento")
            else:
                status_text.text(f"❌ {modelo_nome} não disponível")
            continue
    
    # Limpar progresso
    progress_bar.empty()
    status_text.empty()
    
    # Verificar se algum modelo funcionou
    if model is None:
        st.error("❌ NENHUM MODELO DISPONÍVEL NO MOMENTO")
        st.info("""
        ⏰ **O plano gratuito do Gemini tem cotas diárias que resetam.**
        
        **O que fazer:**
        1. Aguarde algumas horas e tente novamente
        2. Configure faturamento no Google Cloud para limites maiores
        3. Use uma API key diferente se tiver
        
        As cotas geralmente resetam à meia-noite (horário do Pacífico).
        """)
        st.stop()
    
    # The Odds API
    ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"
    ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
    
    st.success(f"✅ APIs configuradas! Modelo ativo: **{modelo_escolhido}**")
    
except Exception as e:
    st.error(f"Erro crítico na configuração: {e}")
    st.stop()

# ============================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================

def processar_csv_com_aspas(arquivo):
    """Processa CSV que tem aspas duplas no início e fim"""
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


def calcular_metricas_comportamentais(df):
    """Calcula todas as métricas de comportamento do jogador"""
    
    metricas = {}
    
    # 1. Análise de valores
    if 'Total stake' in df.columns:
        metricas['total_apostas'] = len(df)
        metricas['valor_medio'] = df['Total stake'].mean()
        metricas['valor_min'] = df['Total stake'].min()
        metricas['valor_max'] = df['Total stake'].max()
        metricas['apostas_495'] = len(df[df['Total stake'] == 495.00])
        metricas['percentual_495'] = (metricas['apostas_495'] / len(df)) * 100 if len(df) > 0 else 0
    
    # 2. Análise de ligas
    if 'Bet champs' in df.columns:
        ligas_suspeitas = ['Vietnam', 'Indonésia', 'Mianmar', 'Camboja', 'Laos', 
                          'Filipinas', 'Timor', 'Brunei', 'Singapura', 'Tailândia',
                          'Malásia', 'Myanmar']
        padrao = '|'.join(ligas_suspeitas)
        metricas['apostas_ligas_suspeitas'] = len(df[df['Bet champs'].str.contains(padrao, case=False, na=False)])
        metricas['ligas_unicas'] = df['Bet champs'].nunique()
        metricas['top_ligas'] = df['Bet champs'].value_counts().head(3).to_dict()
    
    # 3. Análise de odds
    if 'Bet prices' in df.columns:
        df['odds_quebradas'] = df['Bet prices'].apply(
            lambda x: len(str(x).split('.')[-1]) > 2 if '.' in str(x) else False
        )
        metricas['apostas_odds_quebradas'] = len(df[df['odds_quebradas'] == True])
        metricas['odds_media'] = df['Bet prices'].mean()
        metricas['odds_min'] = df['Bet prices'].min()
        metricas['odds_max'] = df['Bet prices'].max()
    
    # 4. Análise temporal
    if 'Created date' in df.columns:
        df['hora'] = df['Created date'].dt.hour
        df['dia_semana'] = df['Created date'].dt.day_name()
        df['minuto_exato'] = df['Created date'].dt.floor('min')
        
        metricas['apostas_madrugada'] = len(df[df['hora'].between(0, 5)])
        
        # Apostas em lote
        apostas_por_minuto = df.groupby('minuto_exato').size()
        minutos_lote = apostas_por_minuto[apostas_por_minuto > 2]
        metricas['apostas_em_lote'] = minutos_lote.sum() if len(minutos_lote) > 0 else 0
        metricas['total_minutos_lote'] = len(minutos_lote)
    
    # 5. Late odds
    if 'Bet event date' in df.columns and 'Created date' in df.columns:
        df['tempo_antecedencia'] = (df['Bet event date'] - df['Created date']).dt.total_seconds() / 3600
        ultima_hora = df[df['tempo_antecedencia'] <= 1]
        metricas['apostas_ultima_hora'] = len(ultima_hora)
        
        if len(ultima_hora) > 0:
            eventos_repetidos = ultima_hora.groupby('Bet events').size()
            metricas['eventos_com_multiplas_apostas'] = len(eventos_repetidos[eventos_repetidos > 1])
        else:
            metricas['eventos_com_multiplas_apostas'] = 0
    
    # 6. Taxa de acerto
    if 'Bet status' in df.columns:
        metricas['apostas_ganhas'] = len(df[df['Bet status'] == 'Ganha'])
        metricas['apostas_perdidas'] = len(df[df['Bet status'] == 'Perdida'])
        metricas['taxa_acerto'] = (metricas['apostas_ganhas'] / len(df)) * 100 if len(df) > 0 else 0
    
    return metricas


def validar_odds_com_api(df, odds_api_key):
    """Valida odds usando The Odds API"""
    
    mapping = {
        'Premier League': 'soccer_epl',
        'La Liga': 'soccer_spain_la_liga',
        'Brasileirão': 'soccer_brazil_campeonato',
        'Serie A': 'soccer_italy_serie_a',
        'Bundesliga': 'soccer_germany_bundesliga',
        'Champions League': 'soccer_uefa_champs_league',
        'Liga Europa': 'soccer_uefa_europa_league'
    }
    
    odds_inconsistentes = []
    
    # Limitar para não gastar muitos créditos
    df_amostra = df.head(20)
    
    with st.spinner("🔍 Validando odds com The Odds API..."):
        progress_bar = st.progress(0)
        
        for idx, aposta in df_amostra.iterrows():
            progress_bar.progress((idx + 1) / len(df_amostra))
            
            liga = aposta.get('Bet champs', '')
            sport_key = mapping.get(liga)
            
            if sport_key:
                try:
                    url = f"{ODDS_BASE_URL}/sports/{sport_key}/odds"
                    params = {
                        "apiKey": odds_api_key,
                        "regions": "eu,uk,br",
                        "markets": "h2h",
                        "oddsFormat": "decimal"
                    }
                    
                    response = requests.get(url, params=params, timeout=5)
                    
                    if response.status_code == 200:
                        eventos = response.json()
                        odds_apostada = float(aposta['Bet prices'])
                        nome_evento = aposta['Bet events']
                        
                        # Procurar evento correspondente
                        for evento in eventos:
                            evento_nome = f"{evento['home_team']} vs {evento['away_team']}"
                            if any(time.lower() in nome_evento.lower() for time in [evento['home_team'], evento['away_team']]):
                                
                                # Coletar odds do mercado
                                odds_list = []
                                for bookmaker in evento.get('bookmakers', []):
                                    for market in bookmaker.get('markets', []):
                                        for outcome in market.get('outcomes', []):
                                            odds_list.append(outcome['price'])
                                
                                if odds_list:
                                    odds_media = sum(odds_list) / len(odds_list)
                                    desvio = ((odds_apostada - odds_media) / odds_media) * 100
                                    
                                    if abs(desvio) > 15:  # Desvio significativo
                                        odds_inconsistentes.append({
                                            'Bet ID': aposta['Bet id'],
                                            'Evento': nome_evento,
                                            'Odds Apostada': odds_apostada,
                                            'Odds Média': round(odds_media, 2),
                                            'Desvio %': round(desvio, 1),
                                            'Classificação': '🚨 MUITO ACIMA' if desvio > 15 else '⚠️ MUITO ABAIXO'
                                        })
                                break
                    
                    time.sleep(0.2)  # Delay para não sobrecarregar
                    
                except Exception as e:
                    continue
        
        progress_bar.empty()
    
    return odds_inconsistentes


# ============================================
# INTERFACE PRINCIPAL
# ============================================

st.markdown("### 📤 Upload da Betlist")
uploaded_file = st.file_uploader(
    "Arraste ou selecione o arquivo CSV/Excel",
    type=['csv', 'xlsx'],
    help="Formatos aceitos: CSV, XLSX"
)

if uploaded_file is not None:
    try:
        # Carregar dados
        if uploaded_file.name.endswith('.csv'):
            df = processar_csv_com_aspas(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado! {len(df)} apostas")
        
        # Identificar jogador
        if 'Player name' in df.columns:
            jogador = df['Player name'].iloc[0]
            st.markdown(f"### 📊 Analisando jogador: **{jogador}**")
        
        with st.expander("👁️ Visualizar dados brutos"):
            st.dataframe(df.head(10))
        
        # Opção de validação com API
        validar_api = st.checkbox("🔍 Validar odds com The Odds API", value=True)
        
        # Tabs organizadas
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Visão Geral",
            "🎲 Análise de Odds",
            "🌏 Padrões Geográficos",
            "🚨 Alertas"
        ])
        
        with tab1:
            # Cards de métricas
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Total stake' in df.columns:
                    card_metrica(
                        "Total Apostas",
                        f"{len(df)}",
                        f"Período: {df['Created date'].min().strftime('%d/%m') if 'Created date' in df.columns else 'N/A'} a {df['Created date'].max().strftime('%d/%m') if 'Created date' in df.columns else 'N/A'}"
                    )
                    
                    card_metrica(
                        "Valor Total",
                        f"R$ {df['Total stake'].sum():,.2f}",
                        f"Média: R$ {df['Total stake'].mean():.2f}"
                    )
            
            with col2:
                if 'Bet status' in df.columns:
                    ganhas = len(df[df['Bet status'] == 'Ganha'])
                    taxa = (ganhas / len(df)) * 100
                    card_metrica(
                        "Taxa de Acerto",
                        f"{taxa:.1f}%",
                        f"{ganhas} ganhas / {len(df)-ganhas} perdidas"
                    )
                
                card_metrica(
                    "Modelo Ativo",
                    modelo_escolhido.split('/')[-1] if modelo_escolhido else "N/A",
                    "Gemini"
                )
            
            # Gráficos
            if 'hora' in df.columns:
                fig = grafico_distribuicao_horarios(df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if 'Total stake' in df.columns:
                    fig = grafico_distribuicao_valores(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            with col_g2:
                if 'Bet champs' in df.columns:
                    fig = grafico_top_ligas(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if 'Bet prices' in df.columns:
                st.subheader("🎲 Análise de Odds")
                
                col_o1, col_o2, col_o3 = st.columns(3)
                with col_o1:
                    card_metrica("Odds Média", f"{df['Bet prices'].mean():.2f}")
                with col_o2:
                    card_metrica("Odds Máxima", f"{df['Bet prices'].max():.2f}")
                with col_o3:
                    card_metrica("Odds Mínima", f"{df['Bet prices'].min():.2f}")
        
        with tab3:
            if 'Bet champs' in df.columns:
                st.subheader("🌏 Distribuição por Liga")
                ligas_df = df['Bet champs'].value_counts().reset_index()
                ligas_df.columns = ['Liga', 'Quantidade']
                st.dataframe(ligas_df, use_container_width=True)
        
        with tab4:
            st.subheader("🚨 Alertas Detectados")
            
            # Detectar padrões suspeitos
            if 'Total stake' in df.columns:
                apostas_495 = len(df[df['Total stake'] == 495.00])
                if apostas_495 > 0:
                    alerta("ALTO", "Valor Fixo Suspeito", 
                          f"{apostas_495} apostas de R$ 495,00 detectadas")
        
        # Botão de análise completa
        if st.button("🚀 INICIAR ANÁLISE COMPLETA", use_container_width=True):
            with st.spinner("🔍 DeepRisk analisando padrões comportamentais..."):
                
                # Calcular métricas
                metricas = calcular_metricas_comportamentais(df)
                
                # Validar odds com API
                odds_inconsistentes = []
                if validar_api:
                    odds_inconsistentes = validar_odds_com_api(df, ODDS_API_KEY)
                
                # Preparar prompt para IA
                prompt = f"""
Você é um especialista sênior em integridade de apostas esportivas da Altenar.

ANÁLISE COMPORTAMENTAL DO JOGADOR:
===================================
Total de apostas: {metricas.get('total_apostas', 0)}
Taxa de acerto: {metricas.get('taxa_acerto', 0):.1f}%
Apostas R$495: {metricas.get('apostas_495', 0)} ({metricas.get('percentual_495', 0):.1f}%)
Ligas suspeitas: {metricas.get('apostas_ligas_suspeitas', 0)}
Odds quebradas: {metricas.get('apostas_odds_quebradas', 0)}
Apostas última hora: {metricas.get('apostas_ultima_hora', 0)}
Eventos repetidos: {metricas.get('eventos_com_multiplas_apostas', 0)}

ODDS INCONSISTENTES: {len(odds_inconsistentes)}

Com base nestes dados, forneça:
1. Perfil do jogador (RECREATIVO, PROFISSIONAL, ARBITRADOR ou CRÍTICO)
2. Principais riscos identificados
3. Recomendações de ação específicas
"""
                
                # Chamar IA
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório Gerado")
                    st.info(response.text)
                    st.balloons()
                    
                    # Mostrar odds inconsistentes se houver
                    if odds_inconsistentes:
                        with st.expander("🚨 Detalhes das odds inconsistentes", expanded=True):
                            st.warning(f"**{len(odds_inconsistentes)} odds inconsistentes detectadas!**")
                            df_odds = pd.DataFrame(odds_inconsistentes)
                            st.dataframe(df_odds, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
        
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        st.exception(e)

else:
    # Estado inicial com cards bonitos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        card_metrica(
            "Total Análises",
            "247",
            "Últimos 30 dias",
            "📊"
        )
    
    with col2:
        card_metrica(
            "Alertas Ativos",
            "3",
            "2 críticos",
            "🚨"
        )
    
    with col3:
        card_metrica(
            "Economia",
            "R$ 5.240",
            "+12% este mês",
            "💰"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 50px; background: linear-gradient(135deg, #1E1E2E20 0%, #2D2D4420 100%); border-radius: 20px; border: 1px dashed #3D3D5C;">
        <h3 style="color: #9D9DFF;">📤 Aguardando Upload</h3>
        <p style="color: #CCCCCC;">Arraste um arquivo CSV ou Excel para iniciar a análise</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
# ============================================

footer_profissional()
