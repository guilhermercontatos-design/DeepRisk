import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import time
import csv
from io import StringIO
import chardet
import re
import requests
import numpy as np
from scipy import stats

# ============================================
# FUNÇÃO 1: LEITOR UNIVERSAL DE PLANILHAS
# ============================================
def processar_planilha_universal(arquivo):
    """LEITOR UNIVERSAL - Aceita qualquer formato de planilha"""
    
    nome_arquivo = arquivo.name.lower()
    
    # Se for Excel
    if nome_arquivo.endswith('.xlsx') or nome_arquivo.endswith('.xls'):
        try:
            df = pd.read_excel(arquivo)
            st.success(f"✅ Excel lido com sucesso! {len(df)} linhas")
            return df
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
            return None
    
    # Se for CSV
    else:
        # Detectar encoding
        conteudo_bruto = arquivo.read()
        try:
            encoding = chardet.detect(conteudo_bruto)['encoding'] or 'utf-8'
            conteudo = conteudo_bruto.decode(encoding)
        except:
            conteudo = conteudo_bruto.decode('latin1')
        
        # Detectar separador
        primeira_linha = conteudo.split('\n')[0] if conteudo else ''
        separadores = [',', ';', '\t', '|']
        separador = ','
        maior = 0
        for sep in separadores:
            if primeira_linha.count(sep) > maior:
                maior = primeira_linha.count(sep)
                separador = sep
        
        # Tentar ler com pandas
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(conteudo), sep=separador, engine='python', 
                           skipinitialspace=True, on_bad_lines='skip')
            st.success(f"✅ CSV lido com sucesso! {len(df)} linhas")
            return df
        except:
            # Leitura manual como fallback
            linhas = [l.strip() for l in conteudo.split('\n') if l.strip()]
            if not linhas:
                return None
            
            cabecalho = [h.strip().strip('"') for h in linhas[0].split(separador)]
            dados = []
            for linha in linhas[1:]:
                valores = [v.strip().strip('"') for v in linha.split(separador)]
                if len(valores) == len(cabecalho):
                    dados.append(valores)
            
            if dados:
                return pd.DataFrame(dados, columns=cabecalho)
            return None

# ============================================
# FUNÇÃO 2: NORMALIZADOR DE COLUNAS
# ============================================
def normalizar_colunas(df):
    """Normaliza os nomes das colunas para o padrão DeepRisk"""
    
    # Mapeamento de nomes possíveis para o padrão
    mapping = {
        'player': 'Player name',
        'player name': 'Player name',
        'nome': 'Player name',
        'jogador': 'Player name',
        
        'bet id': 'Bet id',
        'id': 'Bet id',
        'aposta id': 'Bet id',
        
        'created date': 'Created date',
        'data': 'Created date',
        'data aposta': 'Created date',
        
        'bet event date': 'Bet event date',
        'event date': 'Bet event date',
        'data evento': 'Bet event date',
        
        'bet sports': 'Bet sports',
        'sports': 'Bet sports',
        'esporte': 'Bet sports',
        
        'bet champs': 'Bet champs',
        'champs': 'Bet champs',
        'liga': 'Bet champs',
        'campeonato': 'Bet champs',
        
        'bet events': 'Bet events',
        'events': 'Bet events',
        'evento': 'Bet events',
        'jogo': 'Bet events',
        
        'bet markets': 'Bet markets',
        'markets': 'Bet markets',
        'mercado': 'Bet markets',
        
        'bet prices': 'Bet prices',
        'prices': 'Bet prices',
        'odds': 'Bet prices',
        'cota': 'Bet prices',
        
        'total stake': 'Total stake',
        'stake': 'Total stake',
        'valor': 'Total stake',
        'aposta': 'Total stake',
        
        'bet status': 'Bet status',
        'status': 'Bet status',
        'resultado': 'Bet status'
    }
    
    # Colunas que queremos no final
    colunas_esperadas = [
        'Player name', 'Bet id', 'Created date', 'Bet event date',
        'Bet sports', 'Bet champs', 'Bet events', 'Bet markets', 
        'Bet prices', 'Total stake', 'Bet status'
    ]
    
    # Criar novo DataFrame com colunas normalizadas
    novo_df = pd.DataFrame()
    
    for col_esperada in colunas_esperadas:
        encontrada = False
        
        # Procurar correspondência exata
        if col_esperada in df.columns:
            novo_df[col_esperada] = df[col_esperada]
            encontrada = True
        else:
            # Procurar correspondência aproximada
            for col_original in df.columns:
                col_clean = re.sub(r'[^a-zA-Z]', '', col_original.lower())
                for chave, valor in mapping.items():
                    chave_clean = re.sub(r'[^a-zA-Z]', '', chave.lower())
                    if chave_clean in col_clean or col_clean in chave_clean:
                        novo_df[col_esperada] = df[col_original]
                        encontrada = True
                        break
                if encontrada:
                    break
        
        # Se não encontrou, criar coluna vazia
        if not encontrada:
            novo_df[col_esperada] = None
    
    return novo_df

# ============================================
# FUNÇÃO 3: ANALISADOR SIMPLES (sem precisar dos arquivos core)
# ============================================
def analisar_padroes_simples(df):
    """Análise básica de padrões sem precisar dos arquivos core"""
    
    alertas = []
    pontuacao = 0
    
    # 1. Analisar valores de aposta
    if 'Total stake' in df.columns:
        valores = pd.to_numeric(df['Total stake'], errors='coerce')
        
        # Verificar R$ 495
        count_495 = len(valores[valores == 495.00])
        if count_495 > 0:
            percentual = (count_495 / len(df)) * 100
            alertas.append({
                'severidade': 'ALTA' if percentual > 50 else 'MÉDIA',
                'titulo': '💰 Valores de R$ 495,00',
                'descricao': f'{count_495} apostas ({percentual:.1f}%) com valor R$ 495,00'
            })
            pontuacao += 3 if percentual > 50 else 2
    
    # 2. Analisar ligas
    if 'Bet champs' in df.columns:
        ligas_suspeitas = ['Vietnam', 'Indonésia', 'Mianmar', 'Camboja', 'Laos']
        count_ligas = 0
        for liga in ligas_suspeitas:
            count_ligas += len(df[df['Bet champs'].str.contains(liga, case=False, na=False)])
        
        if count_ligas > 0:
            percentual = (count_ligas / len(df)) * 100
            alertas.append({
                'severidade': 'ALTA' if percentual > 30 else 'MÉDIA',
                'titulo': '🌏 Ligas de Baixa Liquidez',
                'descricao': f'{count_ligas} apostas ({percentual:.1f}%) em ligas suspeitas'
            })
            pontuacao += 3 if percentual > 30 else 2
    
    # 3. Analisar odds quebradas
    if 'Bet prices' in df.columns:
        odds = pd.to_numeric(df['Bet prices'], errors='coerce')
        quebradas = odds.apply(lambda x: len(str(x).split('.')[-1]) > 2 if '.' in str(x) else False)
        count_quebradas = quebradas.sum()
        
        if count_quebradas > 0:
            percentual = (count_quebradas / len(df)) * 100
            alertas.append({
                'severidade': 'MÉDIA' if percentual > 30 else 'BAIXA',
                'titulo': '🎲 Odds Quebradas',
                'descricao': f'{count_quebradas} apostas ({percentual:.1f}%) com odds quebradas'
            })
            pontuacao += 2 if percentual > 30 else 1
    
    # 4. Analisar taxa de acerto
    if 'Bet status' in df.columns:
        ganhas = len(df[df['Bet status'].str.contains('Ganha', case=False, na=False)])
        taxa = (ganhas / len(df)) * 100 if len(df) > 0 else 0
        
        if taxa > 65:
            alertas.append({
                'severidade': 'CRÍTICA',
                'titulo': '📊 Taxa de Acerto Anormal',
                'descricao': f'Taxa de acerto de {taxa:.1f}% ({ganhas} ganhas em {len(df)})'
            })
            pontuacao += 5
        elif taxa > 55:
            alertas.append({
                'severidade': 'MÉDIA',
                'titulo': '📊 Taxa de Acerto Elevada',
                'descricao': f'Taxa de acerto de {taxa:.1f}%'
            })
            pontuacao += 2
    
    # Classificar perfil
    if pontuacao > 10:
        perfil = "🚨 CRÍTICO - ARBITRAGEM PROFISSIONAL"
    elif pontuacao > 5:
        perfil = "⚠️ ALTO - PROFISSIONAL"
    elif pontuacao > 2:
        perfil = "🔍 MÉDIO - ATENÇÃO"
    else:
        perfil = "✅ RECREATIVO - BAIXO RISCO"
    
    return {
        'perfil': perfil,
        'pontuacao': pontuacao,
        'alertas': alertas
    }

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="DeepRisk",
    page_icon="🛡️",
    layout="wide"
)

# Título
st.markdown("""
<h1 style="color: #1A2B3C; font-size: 36px; font-weight: 600; text-align: center;">
    🛡️ DeepRisk
</h1>
<p style="color: #5D6D7E; font-size: 16px; text-align: center; margin-bottom: 30px;">
    Auditoria de Integridade em Apostas Esportivas
</p>
""", unsafe_allow_html=True)

# ============================================
# UPLOAD DO ARQUIVO
# ============================================
uploaded_file = st.file_uploader(
    "📤 Selecione a planilha de apostas",
    type=['csv', 'xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        # Ler a planilha
        df = processar_planilha_universal(uploaded_file)
        
        if df is None or df.empty:
            st.error("Não foi possível ler o arquivo")
            st.stop()
        
        # Normalizar colunas
        df = normalizar_colunas(df)
        
        st.success(f"✅ Arquivo processado! {len(df)} apostas encontradas")
        
        # Mostrar preview
        with st.expander("👁️ Ver dados"):
            st.dataframe(df.head(10))
        
        # Informações básicas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Apostas", len(df))
        with col2:
            if 'Total stake' in df.columns:
                st.metric("Total Apostado", f"R$ {pd.to_numeric(df['Total stake'], errors='coerce').sum():,.2f}")
        with col3:
            if 'Bet status' in df.columns:
                ganhas = len(df[df['Bet status'].str.contains('Ganha', case=False, na=False)])
                st.metric("Taxa Acerto", f"{(ganhas/len(df)*100):.1f}%")
        
        # Botão de análise
        if st.button("🔍 INICIAR ANÁLISE", use_container_width=True):
            
            with st.spinner("Analisando padrões..."):
                
                # Analisar
                resultado = analisar_padroes_simples(df)
                
                # Mostrar resultado
                st.markdown("---")
                st.markdown("## 📊 RESULTADO DA ANÁLISE")
                
                # Perfil
                if "CRÍTICO" in resultado['perfil']:
                    st.error(f"### {resultado['perfil']}")
                elif "ALTO" in resultado['perfil']:
                    st.warning(f"### {resultado['perfil']}")
                elif "MÉDIO" in resultado['perfil']:
                    st.info(f"### {resultado['perfil']}")
                else:
                    st.success(f"### {resultado['perfil']}")
                
                # Alertas
                if resultado['alertas']:
                    st.markdown("### 🚨 Alertas Detectados")
                    for alerta in resultado['alertas']:
                        if alerta['severidade'] == 'CRÍTICA':
                            st.error(f"**{alerta['titulo']}** - {alerta['descricao']}")
                        elif alerta['severidade'] == 'ALTA':
                            st.warning(f"**{alerta['titulo']}** - {alerta['descricao']}")
                        else:
                            st.info(f"**{alerta['titulo']}** - {alerta['descricao']}")
                else:
                    st.success("✅ Nenhum padrão suspeito detectado")
                
                # Pontuação
                st.metric("Pontuação de Risco", resultado['pontuacao'])
                
                st.balloons()
        
    except Exception as e:
        st.error(f"Erro: {e}")
        st.exception(e)

else:
    # Estado inicial
    st.info("📤 Aguardando upload da planilha")
