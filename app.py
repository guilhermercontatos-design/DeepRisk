import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="DeepRisk - Analisador", layout="wide")
st.title("🛡️ DeepRisk: Auditoria de Risco Avançada")
st.markdown("---")

# 2. Configuração do Gemini
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Configure sua GEMINI_API_KEY nos Secrets do Streamlit!")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # LISTA DE MODELOS DISPONÍVEIS (baseado no seu diagnóstico)
    # Vamos usar o gemini-2.5-pro que é o mais robusto
    MODELO_ESCOLHIDO = 'models/gemini-2.5-pro'
    
    # Alternativas caso o principal falhe:
    MODELOS_ALTERNATIVOS = [
        'models/gemini-2.5-pro',
        'models/gemini-2.5-flash',
        'models/gemini-pro-latest',
        'models/gemini-3-pro-preview',
        'models/gemini-3.1-pro-preview'
    ]
    
    model = None
    modelo_ativo = None
    
    # Tentar conectar com o modelo principal
    for modelo in [MODELO_ESCOLHIDO] + MODELOS_ALTERNATIVOS:
        try:
            st.write(f"🔄 Tentando conectar com: {modelo}...")
            model = genai.GenerativeModel(modelo)
            # Teste rápido
            test = model.generate_content("teste", generation_config={"max_output_tokens": 1})
            modelo_ativo = modelo
            st.success(f"✅ Conectado com sucesso: {modelo}")
            break
        except Exception as e:
            st.write(f"❌ {modelo} não disponível: {str(e)[:50]}")
            continue
    
    if model is None:
        st.error("❌ Nenhum modelo disponível! Verifique sua chave de API.")
        st.stop()
    
except Exception as e:
    st.error(f"Erro na configuração: {e}")
    st.stop()

# 3. Interface de Upload
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Suba sua planilha de apostas Altenar (CSV ou Excel)", 
        type=['csv', 'xlsx']
    )

with col2:
    st.info(f"🤖 Modelo ativo: **{modelo_ativo.split('/')[-1]}**")

if uploaded_file is not None:
    try:
        # Carregamento inteligente
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado! **{len(df)}** linhas identificadas.")
        
        with st.expander("👁️ Visualizar dados brutos", expanded=False):
            st.dataframe(df.head(20))
            st.caption(f"Mostrando 20 de {len(df)} linhas")

        # 4. Botão de Auditoria
        if st.button("🚀 Iniciar Auditoria IA", type="primary", use_container_width=True):
            with st.spinner(f"DeepRisk analisando padrões de risco com {modelo_ativo.split('/')[-1]}..."):
                try:
                    # Preparar dados (limitar para não exceder tokens)
                    dados_analise = df.head(100).to_string()
                    
                    prompt = f"""Você é um especialista sênior em integridade de apostas esportivas da Altenar.

ANÁLISE DE DADOS DE APOSTAS:
{dados_analise}

INSTRUÇÕES ESPECÍFICAS:
Analise os dados acima e identifique comportamentos suspeitos, focando em:

1. **VALORES SUSPEITOS**: Apostas recorrentes próximas a R$ 495,00 (possível tentativa de burlar limites)
2. **MERCADOS ATÍPICOS**: Concentração anormal em ligas de baixa liquidez (Vietnã, Indonésia, ligas secundárias)
3. **PADRÕES DE ARBITRAGEM**: Uso de centavos quebrados, valores inconsistentes com apostas comuns
4. **PADRÕES TEMPORAIS**: Horários atípicos, frequência anormal de apostas
5. **CONCENTRAÇÃO**: Mesmos usuários apostando repetidamente nos mesmos mercados

FORMATO DO RELATÓRIO:

📊 **RESUMO EXECUTIVO**
[Breve resumo das descobertas]

🔍 **PADRÕES IDENTIFICADOS**
- Padrão 1: [descrição e evidências]
- Padrão 2: [descrição e evidências]
- Padrão 3: [descrição e evidências]

⚠️ **NÍVEL DE RISCO**
[RECREATIVO | PROFISSIONAL | SUSPEITO | CRÍTICO]

🎯 **RECOMENDAÇÕES**
- Recomendação 1
- Recomendação 2
- Recomendação 3

---
Relatório gerado por DeepRisk IA em {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
                    
                    # Chamada ao modelo
                    response = model.generate_content(prompt)
                    
                    # Mostrar resultado
                    st.markdown("### 📊 Relatório de Risco")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # Botões de ação
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            label="📥 Baixar Relatório (TXT)",
                            data=response.text,
                            file_name=f"deeprisk_relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Preparar CSV com alertas
                        alertas_df = df.head(100).copy()
                        csv = alertas_df.to_csv(index=False)
                        st.download_button(
                            label="📊 Baixar Dados Analisados",
                            data=csv,
                            file_name=f"dados_analisados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col3:
                        if st.button("🔄 Nova Análise", use_container_width=True):
                            st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro na geração do relatório: {e}")
                    
                    # Sugestões de troubleshooting
                    with st.expander("🔧 Opções de recuperação"):
                        st.write("Tente:")
                        st.write("1. Reduzir o número de linhas analisadas")
                        st.write("2. Verificar formatação dos dados")
                        st.write("3. Tentar outro modelo")
                        
                        # Botão para tentar com modelo alternativo
                        if st.button("🔄 Tentar com modelo alternativo"):
                            st.rerun()
                    
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        st.exception(e)
else:
    # Estado inicial sem arquivo
    st.info("📤 Arraste e solte um arquivo CSV ou Excel para começar")
    
    # Exemplo de formato esperado
    with st.expander("📋 Formato esperado dos dados"):
        st.markdown("""
        O arquivo deve conter colunas como:
        - **Data/Hora** da aposta
        - **Valor** da aposta
        - **Liga/Competição**
        - **Usuário/ID** (opcional)
        - **Mercado** (opcional)
        
        Formatos aceitos: CSV (separado por vírgula ou ponto e vírgula) ou Excel
        """)

# Rodapé
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"DeepRisk v2.0 - Python 3.11")
with col2:
    st.caption(f"🤖 Modelo: {modelo_ativo.split('/')[-1] if model else 'Não conectado'}")
with col3:
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
