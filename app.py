import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import requests
import time

# 1. Configurações da Página
st.set_page_config(page_title="DeepRisk - Analisador", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco Avançada")
st.markdown("---")

# 2. Configuração das APIs com FALLBACK AUTOMÁTICO
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRO: Configure sua GEMINI_API_KEY nos Secrets.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # LISTA DE MODELOS PARA TENTAR (do mais novo ao mais antigo)
    modelos_para_tentar = [
        'models/gemini-2.0-flash',      # Modelo recomendado - boas cotas
        'models/gemini-1.5-flash',       # Modelo original que funcionava
        'models/gemini-pro',              # Modelo mais básico e estável
        'models/gemini-1.0-pro',          # Versão ainda mais antiga
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
            
            # Se for erro de cota (429), tenta o próximo
            if "429" in erro_msg or "quota" in erro_msg.lower():
                status_text.text(f"⚠️ {modelo_nome} sem cota disponível")
            else:
                status_text.text(f"❌ {modelo_nome} não disponível")
            continue
    
    # Limpar progresso
    progress_bar.empty()
    status_text.empty()
    
    # Verificar se algum modelo funcionou
    if model is None:
        st.error("❌ NENHUM MODELO DISPONÍVEL!")
        st.write("Motivos dos erros:")
        for erro in erros_encontrados:
            st.write(f"- {erro}")
        st.info("💡 Soluções:\n1. Aguarde alguns minutos (cotas resetam)\n2. Configure faturamento no Google Cloud\n3. Tente novamente mais tarde")
        st.stop()
    
    # The Odds API
    ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"
    ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
    
    st.success(f"✅ APIs configuradas! Modelo ativo: **{modelo_escolhido}**")
    
except Exception as e:
    st.error(f"Erro crítico na configuração: {e}")
    st.stop()

# 3. Função para processar CSV com aspas
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

# 4. Função para calcular métricas comportamentais
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

# 5. Função para validar odds com API
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

# 6. Interface de Upload
uploaded_file = st.file_uploader("Suba sua planilha de apostas Altenar (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carregamento inteligente dos dados
        if uploaded_file.name.endswith('.csv'):
            df = processar_csv_com_aspas(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado com sucesso! {len(df)} linhas identificadas.")
        
        # Identificar jogador
        if 'Player name' in df.columns:
            jogador = df['Player name'].iloc[0]
            st.subheader(f"📊 Analisando jogador: **{jogador}**")
        
        with st.expander("👁️ Clique para conferir os dados brutos"):
            st.dataframe(df.head(20))
        
        # Opções de análise
        col1, col2 = st.columns([3, 1])
        with col1:
            validar_com_api = st.checkbox("🔍 Validar odds com The Odds API (recomendado)", value=True)
        with col2:
            st.info(f"🎯 {len(df)} apostas no período")
        
        # 7. Botão de Auditoria
        if st.button("🚀 Iniciar Auditoria IA", type="primary", use_container_width=True):
            with st.spinner(f"O DeepRisk está processando os padrões de risco usando {modelo_escolhido}..."):
                
                # Calcular métricas comportamentais
                metricas = calcular_metricas_comportamentais(df)
                
                # Validar odds com API se solicitado
                odds_inconsistentes = []
                if validar_com_api:
                    odds_inconsistentes = validar_odds_com_api(df, ODDS_API_KEY)
                
                # Preparar dados para a IA
                dados_audit = df.head(50).to_string()
                
                # Construir prompt com todas as métricas
                prompt = f"""
Você é um especialista sênior em integridade de apostas esportivas da Altenar.

ANÁLISE COMPORTAMENTAL DO JOGADOR:
===================================
Total de apostas: {metricas.get('total_apostas', 0)}
Período analisado: {df['Created date'].min().strftime('%d/%m/%Y') if 'Created date' in df.columns else 'N/A'} a {df['Created date'].max().strftime('%d/%m/%Y') if 'Created date' in df.columns else 'N/A'}

📊 **MÉTRICAS DE APOSTAS:**
- Valor médio: R$ {metricas.get('valor_medio', 0):.2f}
- Valor mínimo: R$ {metricas.get('valor_min', 0):.2f}
- Valor máximo: R$ {metricas.get('valor_max', 0):.2f}
- Apostas de R$ 495,00: {metricas.get('apostas_495', 0)} ({metricas.get('percentual_495', 0):.1f}% do total)

🌏 **ANÁLISE DE LIGAS:**
- Apostas em ligas suspeitas: {metricas.get('apostas_ligas_suspeitas', 0)}
- Ligas diferentes: {metricas.get('ligas_unicas', 0)}
- Top 3 ligas: {metricas.get('top_ligas', {})}

🎲 **ANÁLISE DE ODDS:**
- Odds quebradas (arbitragem): {metricas.get('apostas_odds_quebradas', 0)}
- Odds média: {metricas.get('odds_media', 0):.2f}
- Odds mínima: {metricas.get('odds_min', 0):.2f}
- Odds máxima: {metricas.get('odds_max', 0):.2f}

⏰ **ANÁLISE TEMPORAL:**
- Apostas na madrugada (0h-5h): {metricas.get('apostas_madrugada', 0)}
- Apostas em lote (mesmo minuto): {metricas.get('apostas_em_lote', 0)}
- Eventos com múltiplas apostas: {metricas.get('eventos_com_multiplas_apostas', 0)}

⚡ **LATE ODDS:**
- Apostas na última hora: {metricas.get('apostas_ultima_hora', 0)}

📈 **TAXA DE ACERTO:**
- Apostas ganhas: {metricas.get('apostas_ganhas', 0)}
- Apostas perdidas: {metricas.get('apostas_perdidas', 0)}
- Taxa de acerto: {metricas.get('taxa_acerto', 0):.1f}%

"""

                # Adicionar seção de odds inconsistentes se houver
                if odds_inconsistentes:
                    prompt += f"""
🚨 **ODDS INCONSISTENTES DETECTADAS (VALIDAÇÃO COM THE ODDS API):**
Total de odds inconsistentes: {len(odds_inconsistentes)}

Detalhes:
{chr(10).join([f"- Aposta {o['Bet ID']}: {o['Evento']} | Odds: {o['Odds Apostada']} vs Média: {o['Odds Média']} | Desvio: {o['Desvio %']}% {o['Classificação']}" for o in odds_inconsistentes])}

"""

                prompt += """
ANÁLISE COMPORTAMENTAL DETALHADA:
================================
Com base nas métricas acima, analise:

1. **PADRÕES DE VALOR**: Existe concentração em valores específicos? O valor de R$495,00 aparece com frequência?
2. **PADRÕES DE LIGAS**: Há concentração em ligas de baixa liquidez? Quais?
3. **PADRÕES DE ODDS**: As odds são quebradas (padrão de arbitragem)?
4. **PADRÕES TEMPORAIS**: O jogador aposta em horários atípicos? Faz apostas em lote?
5. **LATE ODDS**: Aposta muito próximo ao início dos eventos?
6. **TAXA DE ACERTO**: Está dentro do normal (45-55%) ou muito acima?
"""

                if odds_inconsistentes:
                    prompt += """
7. **ODDS ERRADAS**: As odds inconsistentes detectadas indicam exploração de latência/erros do sistema?
"""

                prompt += """
Com base em TODOS os padrões identificados, forneça:

📋 **RELATÓRIO EXECUTIVO:**
- Perfil do jogador (RECREATIVO, PROFISSIONAL, ARBITRADOR ou CRÍTICO)
- Principais padrões de risco identificados
- Evidências concretas dos padrões

⚠️ **NÍVEL DE RISCO:**
[BAIXO | MÉDIO | ALTO | CRÍTICO]

🎯 **RECOMENDAÇÕES DE AÇÃO:**
- O que fazer com este jogador?
- Precisa de monitoramento?
- Deve ser bloqueado?

Responda em Português, seja detalhado e profissional.
"""

                # Chamada à IA (com retry automático)
                tentativas = 0
                max_tentativas = 3
                response = None
                
                while tentativas < max_tentativas and response is None:
                    try:
                        response = model.generate_content(prompt)
                    except Exception as e:
                        tentativas += 1
                        if tentativas < max_tentativas:
                            st.warning(f"⚠️ Erro na chamada IA, tentativa {tentativas+1}/{max_tentativas}...")
                            time.sleep(2)
                        else:
                            st.error(f"Erro na IA após {max_tentativas} tentativas: {e}")
                            response = None
                
                # Mostrar relatório
                st.markdown("### 📊 Relatório de Risco Gerado")
                
                if response and hasattr(response, 'text'):
                    st.info(response.text)
                    
                    # Mostrar odds inconsistentes em destaque se houver
                    if odds_inconsistentes:
                        with st.expander("🚨 Detalhes das odds inconsistentes encontradas", expanded=True):
                            st.warning(f"**{len(odds_inconsistentes)} odds inconsistentes detectadas!**")
                            df_odds = pd.DataFrame(odds_inconsistentes)
                            st.dataframe(df_odds, use_container_width=True)
                    
                    # Botão de download
                    relatorio_completo = f"""
RELATÓRIO DEEPRISK - ANÁLISE COMPLETA
======================================
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Jogador: {jogador if 'jogador' in locals() else 'N/A'}
Total de apostas: {len(df)}
Modelo utilizado: {modelo_escolhido}

{response.text}

MÉTRICAS COMPUTACIONAIS:
{chr(10).join([f"{k}: {v}" for k, v in metricas.items()])}

ODDS INCONSISTENTES: {len(odds_inconsistentes)}
"""
                    
                    st.download_button(
                        label="📄 Baixar Relatório Completo",
                        data=relatorio_completo,
                        file_name=f"deeprisk_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Não foi possível gerar o relatório. Tente novamente mais tarde.")
                
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.exception(e)
else:
    st.info("Aguardando upload para iniciar auditoria.")

st.markdown("---")
st.caption(f"DeepRisk v4.0 - Python 3.11 | Modelo ativo: {modelo_escolhido if 'modelo_escolhido' in locals() else 'N/A'} | Com validação The Odds API")
