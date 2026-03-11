import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import numpy as np
import requests

# 1. Configurações da Página
st.set_page_config(page_title="DeepRisk - Analisador Comportamental", layout="wide")
st.title("🛡️ DeepRisk: Auditoria Comportamental Avançada")
st.markdown("---")

# 2. Configuração das APIs
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Configure sua GEMINI_API_KEY nos Secrets do Streamlit!")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    
    # The Odds API (opcional)
    ODDS_API_KEY = "3dd5323db5132e0a04840136ac9f0556"
    
    st.success("✅ APIs configuradas!")
except Exception as e:
    st.error(f"Erro na configuração: {e}")
    st.stop()

# 3. FUNÇÕES DE ANÁLISE COMPORTAMENTAL
class AnalisadorComportamental:
    """Classe que encapsula TODAS as análises de padrões de apostas"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.resultados = {}
        self.padroes_detectados = []
        self._preparar_dados()
    
    def _preparar_dados(self):
        """Prepara os dados para análise"""
        # Converter datas
        for col in ['Created date', 'Bet event date', 'Settlement date']:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Calcular métricas básicas
        if 'Created date' in self.df.columns:
            self.df['hora'] = self.df['Created date'].dt.hour
            self.df['dia_semana'] = self.df['Created date'].dt.day_name()
        
        if 'Bet event date' in self.df.columns and 'Created date' in self.df.columns:
            self.df['tempo_antecedencia'] = (self.df['Bet event date'] - self.df['Created date']).dt.total_seconds() / 3600
    
    def analisar_valores_suspeitos(self, limiar=495.0):
        """Detecta apostas com valores fixos suspeitos"""
        if 'Total stake' not in self.df.columns:
            return
        
        apostas_fixas = self.df[self.df['Total stake'] == limiar]
        
        if len(apostas_fixas) > 0:
            percentual = (len(apostas_fixas) / len(self.df)) * 100
            self.padroes_detectados.append({
                'padrao': '💰 VALOR FIXO SUSPEITO',
                'severidade': 'ALTA' if percentual > 30 else 'MÉDIA' if percentual > 15 else 'BAIXA',
                'descricao': f"{len(apostas_fixas)} apostas com valor R$ {limiar:.2f} ({percentual:.1f}% do total)",
                'dados': apostas_fixas[['Bet id', 'Bet events', 'Total stake', 'Bet status']] if len(apostas_fixas) > 0 else None
            })
    
    def analisar_ligas_baixa_liquidez(self, ligas_suspeitas=None):
        """Detecta concentração em ligas de baixa liquidez"""
        if 'Bet champs' not in self.df.columns:
            return
        
        if ligas_suspeitas is None:
            ligas_suspeitas = ['Vietnam', 'Indonésia', 'Mianmar', 'Camboja', 'Laos', 
                              'Filipinas', 'Timor', 'Brunei', 'Singapura', 'Tailândia',
                              'Malásia', 'Myanmar']
        
        padrao = '|'.join(ligas_suspeitas)
        apostas_suspeitas = self.df[self.df['Bet champs'].str.contains(padrao, case=False, na=False)]
        
        if len(apostas_suspeitas) > 0:
            percentual = (len(apostas_suspeitas) / len(self.df)) * 100
            self.padroes_detectados.append({
                'padrao': '🌏 LIGAS DE BAIXA LIQUIDEZ',
                'severidade': 'ALTA' if percentual > 50 else 'MÉDIA' if percentual > 25 else 'BAIXA',
                'descricao': f"{len(apostas_suspeitas)} apostas em ligas suspeitas ({percentual:.1f}%)",
                'dados': apostas_suspeitas[['Bet id', 'Bet champs', 'Bet events', 'Bet prices']] if len(apostas_suspeitas) > 0 else None
            })
    
    def analisar_odds_quebradas(self):
        """Detecta padrão de arbitragem (odds com muitos decimais)"""
        if 'Bet prices' not in self.df.columns:
            return
        
        self.df['odds_quebradas'] = self.df['Bet prices'].apply(
            lambda x: len(str(x).split('.')[-1]) > 2 if '.' in str(x) else False
        )
        
        apostas_quebradas = self.df[self.df['odds_quebradas'] == True]
        
        if len(apostas_quebradas) > 0:
            percentual = (len(apostas_quebradas) / len(self.df)) * 100
            self.padroes_detectados.append({
                'padrao': '🎲 ODDS QUEBRADAS (ARBITRAGEM)',
                'severidade': 'MÉDIA' if percentual > 40 else 'BAIXA',
                'descricao': f"{len(apostas_quebradas)} apostas com odds quebradas ({percentual:.1f}%)",
                'dados': apostas_quebradas[['Bet id', 'Bet events', 'Bet prices']] if len(apostas_quebradas) > 0 else None
            })
    
    def analisar_padrao_temporal(self):
        """Analisa horários e frequência das apostas"""
        if 'hora' not in self.df.columns:
            return
        
        # Apostas em horário comercial vs madrugada
        apostas_madrugada = self.df[self.df['hora'].between(0, 5)]
        
        if len(apostas_madrugada) > 0:
            percentual = (len(apostas_madrugada) / len(self.df)) * 100
            if percentual > 30:
                self.padroes_detectados.append({
                    'padrao': '🌙 PADRÃO NOTURNO',
                    'severidade': 'MÉDIA',
                    'descricao': f"{len(apostas_madrugada)} apostas entre 0h-5h ({percentual:.1f}%)",
                    'dados': apostas_madrugada[['Bet id', 'Created date', 'Bet events']] if len(apostas_madrugada) > 0 else None
                })
        
        # Apostas em lote (mesmo minuto)
        if 'Created date' in self.df.columns:
            self.df['minuto_exato'] = self.df['Created date'].dt.floor('min')
            apostas_por_minuto = self.df.groupby('minuto_exato').size()
            minutos_lote = apostas_por_minuto[apostas_por_minuto > 2]
            
            if len(minutos_lote) > 0:
                total_apostas_lote = minutos_lote.sum()
                percentual_lote = (total_apostas_lote / len(self.df)) * 100
                if percentual_lote > 20:
                    self.padroes_detectados.append({
                        'padrao': '⏰ APOSTAS EM LOTE',
                        'severidade': 'ALTA',
                        'descricao': f"{total_apostas_lote} apostas feitas no mesmo minuto ({percentual_lote:.1f}%)",
                        'dados': self.df[self.df['minuto_exato'].isin(minutos_lote.index)][['Bet id', 'Created date', 'Bet events']] if len(minutos_lote) > 0 else None
                    })
    
    def analisar_late_odds(self):
        """Detecta apostas de última hora (potencial latência)"""
        if 'tempo_antecedencia' not in self.df.columns:
            return
        
        # Apostas feitas na última hora
        ultima_hora = self.df[self.df['tempo_antecedencia'] <= 1]
        
        if len(ultima_hora) > 0:
            percentual = (len(ultima_hora) / len(self.df)) * 100
            
            # Verificar se o mesmo usuário apostou várias vezes no mesmo evento
            apostas_por_evento = ultima_hora.groupby('Bet events').size()
            eventos_repetidos = apostas_por_evento[apostas_por_evento > 1]
            
            if len(eventos_repetidos) > 0:
                self.padroes_detectados.append({
                    'padrao': '⚡ LATE ODDS EXPLOITATION',
                    'severidade': 'CRÍTICA',
                    'descricao': f"{len(eventos_repetidos)} eventos com múltiplas apostas na última hora",
                    'dados': ultima_hora[ultima_hora['Bet events'].isin(eventos_repetidos.index)][['Bet id', 'Bet events', 'Created date', 'Bet event date', 'Bet prices']] if len(eventos_repetidos) > 0 else None
                })
    
    def analisar_taxa_acerto(self):
        """Analisa se a taxa de acerto é anormalmente alta"""
        if 'Bet status' not in self.df.columns:
            return
        
        total = len(self.df)
        ganhas = len(self.df[self.df['Bet status'] == 'Ganha'])
        taxa_acerto = (ganhas / total) * 100 if total > 0 else 0
        
        if taxa_acerto > 55:  # Acima do normal
            severidade = 'CRÍTICA' if taxa_acerto > 65 else 'ALTA' if taxa_acerto > 60 else 'MÉDIA'
            self.padroes_detectados.append({
                'padrao': '📊 TAXA DE ACERTO ANORMAL',
                'severidade': severidade,
                'descricao': f"Taxa de acerto de {taxa_acerto:.1f}% ({ganhas} ganhas em {total})",
                'dados': None
            })
    
    def gerar_relatorio_completo(self):
        """Executa todas as análises e gera relatório consolidado"""
        
        # Executar todas as análises
        self.analisar_valores_suspeitos()
        self.analisar_ligas_baixa_liquidez()
        self.analisar_odds_quebradas()
        self.analisar_padrao_temporal()
        self.analisar_late_odds()
        self.analisar_taxa_acerto()
        
        # Calcular perfil de risco
        pontuacao_risco = 0
        niveis = {'BAIXA': 1, 'MÉDIA': 2, 'ALTA': 3, 'CRÍTICA': 4}
        
        for padrao in self.padroes_detectados:
            pontuacao_risco += niveis.get(padrao['severidade'], 1)
        
        # Classificar perfil
        if pontuacao_risco > 15:
            perfil = "🚨 CRÍTICO - ARBITRAGEM PROFISSIONAL"
        elif pontuacao_risco > 10:
            perfil = "⚠️ SUSPEITO - PADRÕES PROFISSIONAIS"
        elif pontuacao_risco > 5:
            perfil = "🔍 ATENÇÃO - APOSTADOR FREQUENTE"
        else:
            perfil = "✅ RECREATIVO - SEM PADRÕES SUSPEITOS"
        
        return {
            'perfil': perfil,
            'pontuacao': pontuacao_risco,
            'padroes': self.padroes_detectados,
            'total_apostas': len(self.df)
        }

# 4. INTERFACE PRINCIPAL
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("📤 Suba a betlist do jogador (CSV/Excel)", type=['csv', 'xlsx'])

with col2:
    st.info("""
    **O que será analisado:**
    - 💰 Valores fixos (R$495,00)
    - 🌏 Ligas suspeitas
    - 🎲 Odds quebradas
    - ⏰ Padrões temporais
    - ⚡ Late odds
    - 📊 Taxa de acerto
    """)

if uploaded_file is not None:
    try:
        # Carregar dados - VERSÃO CORRIGIDA para seu formato
        if uploaded_file.name.endswith('.csv'):
            # Ler o arquivo como texto primeiro
            content = uploaded_file.read().decode('utf-8')
            
            # Processar linhas
            lines = content.strip().split('\n')
            
            # Extrair cabeçalho (primeira linha)
            header_line = lines[0].strip()
            if header_line.startswith('"') and header_line.endswith('"'):
                header_line = header_line.strip('"')
            header = header_line.split(',')
            
            # Processar dados
            data = []
            for line in lines[1:]:
                if line.strip():
                    # Limpar a linha
                    clean_line = line.strip()
                    if clean_line.startswith('"') and clean_line.endswith('"'):
                        clean_line = clean_line.strip('"')
                    values = clean_line.split(',')
                    data.append(values)
            
            # Criar DataFrame
            df = pd.DataFrame(data, columns=header)
            
            # Converter colunas numéricas
            for col in ['Bet prices', 'Total stake', 'Real win']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            st.success(f"✅ Betlist carregada! {len(df)} apostas")
            
            with st.expander("👁️ Visualizar dados brutos"):
                st.dataframe(df.head(20))
            
            # Identificar jogador
            if 'Player name' in df.columns:
                jogador = df['Player name'].iloc[0] if len(df) > 0 else "Desconhecido"
                st.markdown(f"## 📊 Análise do Jogador: **{jogador}**")
                st.markdown(f"Total de apostas no período: **{len(df)}**")
                
                # Inicializar analisador
                analisador = AnalisadorComportamental(df)
                
                # Botão para iniciar análise
                if st.button("🚀 INICIAR ANÁLISE COMPLETA", type="primary", use_container_width=True):
                    with st.spinner("Analisando padrões comportamentais..."):
                        
                        # Gerar relatório
                        relatorio = analisador.gerar_relatorio_completo()
                        
                        # MOSTRAR RESULTADOS
                        st.markdown("---")
                        
                        # Perfil de risco
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Perfil de Risco", relatorio['perfil'])
                        with col_b:
                            st.metric("Pontuação", relatorio['pontuacao'])
                        with col_c:
                            st.metric("Apostas Analisadas", relatorio['total_apostas'])
                        
                        st.markdown("---")
                        
                        # Padrões detectados
                        if relatorio['padroes']:
                            st.markdown("## 🔍 PADRÕES DETECTADOS")
                            
                            # Separar por severidade
                            criticos = [p for p in relatorio['padroes'] if p['severidade'] == 'CRÍTICA']
                            altos = [p for p in relatorio['padroes'] if p['severidade'] == 'ALTA']
                            medios = [p for p in relatorio['padroes'] if p['severidade'] == 'MÉDIA']
                            baixos = [p for p in relatorio['padroes'] if p['severidade'] == 'BAIXA']
                            
                            # Mostrar críticos primeiro
                            if criticos:
                                st.markdown("### 🚨 PADRÕES CRÍTICOS")
                                for p in criticos:
                                    with st.expander(f"**{p['padrao']}**", expanded=True):
                                        st.error(p['descricao'])
                                        if p['dados'] is not None:
                                            st.dataframe(p['dados'])
                            
                            if altos:
                                st.markdown("### ⚠️ PADRÕES DE ALTA SEVERIDADE")
                                for p in altos:
                                    with st.expander(f"**{p['padrao']}**"):
                                        st.warning(p['descricao'])
                                        if p['dados'] is not None:
                                            st.dataframe(p['dados'])
                            
                            if medios:
                                st.markdown("### 🔍 PADRÕES DE MÉDIA SEVERIDADE")
                                for p in medios:
                                    with st.expander(f"**{p['padrao']}**"):
                                        st.info(p['descricao'])
                                        if p['dados'] is not None:
                                            st.dataframe(p['dados'])
                            
                            if baixos:
                                st.markdown("### 📌 PADRÕES DE BAIXA SEVERIDADE")
                                for p in baixos:
                                    with st.expander(f"**{p['padrao']}**"):
                                        st.write(p['descricao'])
                                        if p['dados'] is not None:
                                            st.dataframe(p['dados'])
                        else:
                            st.success("✅ Nenhum padrão suspeito detectado!")
                        
                        # Resumo com IA
                        st.markdown("---")
                        st.markdown("### 📋 RESUMO EXECUTIVO")
                        
                        prompt_resumo = f"""
                        Jogador: {jogador}
                        Total de apostas: {relatorio['total_apostas']}
                        Perfil de risco: {relatorio['perfil']}
                        
                        Padrões detectados:
                        {chr(10).join([f"- {p['padrao']} ({p['severidade']}): {p['descricao']}" for p in relatorio['padroes']])}
                        
                        Gere um resumo executivo em português com:
                        1. Perfil do jogador (recreativo, profissional ou arbitrador)
                        2. Principais riscos identificados
                        3. Recomendações de ação
                        """
                        
                        try:
                            response = model.generate_content(prompt_resumo)
                            st.info(response.text)
                        except Exception as e:
                            st.write("Resumo gerado pela análise local")
                        
                        # Botão para download
                        relatorio_texto = f"""
RELATÓRIO DEEPRISK - ANÁLISE COMPORTAMENTAL
=============================================
Jogador: {jogador}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Total de Apostas: {relatorio['total_apostas']}
Perfil: {relatorio['perfil']}
Pontuação de Risco: {relatorio['pontuacao']}

PADRÕES DETECTADOS:
{chr(10).join([f"- {p['padrao']} ({p['severidade']}): {p['descricao']}" for p in relatorio['padroes']])}

RECOMENDAÇÕES:
1. {"🚨 Monitoramento intensivo necessário" if relatorio['pontuacao'] > 10 else "✅ Acompanhamento padrão"}
2. {"🌏 Revisar apostas em ligas asiáticas" if any('LIGAS' in p['padrao'] for p in relatorio['padroes']) else ""}
3. {"⚡ Verificar padrão de late odds" if any('LATE' in p['padrao'] for p in relatorio['padroes']) else ""}
4. {"💰 Investigar valores fixos" if any('VALOR FIXO' in p['padrao'] for p in relatorio['padroes']) else ""}
"""
                        st.download_button(
                            label="📥 Baixar Relatório Completo",
                            data=relatorio_texto,
                            file_name=f"deeprisk_{jogador}_{datetime.now().strftime('%Y%m%d')}.txt"
                        )
            else:
                st.error("❌ Coluna 'Player name' não encontrada na planilha!")
                st.write("Colunas encontradas:", list(df.columns))
                
        else:  # Excel
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ Betlist carregada! {len(df)} apostas")
            
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        st.exception(e)

st.markdown("---")
st.caption("DeepRisk v3.0 - Analisador Comportamental Completo")
