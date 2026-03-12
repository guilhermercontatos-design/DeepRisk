# layout.py - TODOS OS ESTILOS E COMPONENTES VISUAIS
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DE TEMA E CSS
# ============================================

def aplicar_tema_profissional():
    """Aplica todo o CSS personalizado ao app"""
    
    st.markdown("""
    <style>
        /* Tema escuro profissional */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Cards com gradiente */
        .metric-card {
            background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #3D3D5C;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            margin: 10px 0;
            transition: transform 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(75,75,255,0.2);
        }
        
        .metric-title {
            color: #9D9DFF;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }
        
        .metric-value {
            color: white;
            font-size: 32px;
            font-weight: bold;
            margin: 5px 0;
        }
        
        .metric-delta {
            color: #4CAF50;
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Alertas */
        .alert-critical {
            background: linear-gradient(135deg, #FF4B4B20 0%, #FF4B4B10 100%);
            border-left: 5px solid #FF4B4B;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .alert-high {
            background: linear-gradient(135deg, #FFA64B20 0%, #FFA64B10 100%);
            border-left: 5px solid #FFA64B;
            padding: 15px;
            border-radius: 10px;
        }
        
        .alert-medium {
            background: linear-gradient(135deg, #FFD70020 0%, #FFD70010 100%);
            border-left: 5px solid #FFD700;
            padding: 15px;
            border-radius: 10px;
        }
        
        /* Títulos */
        .gradient-title {
            background: linear-gradient(90deg, #9D9DFF, #FF9D9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(90deg, #4B4BFF, #9D4BFF);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: bold;
            transition: all 0.3s;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 25px rgba(75,75,255,0.5);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #1E1E2E;
            padding: 10px;
            border-radius: 15px;
            border: 1px solid #3D3D5C;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 10px 25px;
            background-color: #2D2D44;
            color: #9D9DFF;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #4B4BFF, #9D4BFF);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


def titulo_principal():
    """Renderiza o título principal"""
    st.markdown('<h1 class="gradient-title">🛡️ DeepRisk Professional</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #9D9DFF; margin-bottom: 30px;">Auditoria de Risco e Integridade em Apostas Esportivas</p>', unsafe_allow_html=True)


def card_metrica(titulo, valor, delta=None, icone="📊"):
    """Cria um card de métrica"""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{icone} {titulo}</div>
        <div class="metric-value">{valor}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def alerta(tipo, titulo, mensagem):
    """Renderiza alertas coloridos"""
    if tipo == "CRÍTICO":
        st.markdown(f"""
        <div class="alert-critical">
            <strong>🚨 {titulo}</strong><br>
            {mensagem}
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "ALTO":
        st.markdown(f"""
        <div class="alert-high">
            <strong>⚠️ {titulo}</strong><br>
            {mensagem}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-medium">
            <strong>📌 {titulo}</strong><br>
            {mensagem}
        </div>
        """, unsafe_allow_html=True)


def footer_profissional():
    """Renderiza o rodapé"""
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**🛡️ DeepRisk v4.0**")
        st.caption("© 2026")
    with col2:
        st.markdown("**📧 Suporte**")
        st.caption("suporte@deeprisk.com")
    with col3:
        st.markdown("**🔒 Segurança**")
        st.caption("ISO 27001")
    with col4:
        st.markdown("**📊 Versão**")
        st.caption("Enterprise")


# ============================================
# GRÁFICOS
# ============================================

def grafico_distribuicao_horarios(df):
    """Gráfico de distribuição por horário"""
    if 'hora' not in df.columns:
        return None
        
    fig = px.histogram(
        df, 
        x='hora',
        nbins=24,
        title="📅 Distribuição por Horário",
        labels={'hora': 'Hora do Dia', 'count': 'Qtd Apostas'},
        color_discrete_sequence=['#9D9DFF']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#9D9DFF'
    )
    return fig


def grafico_distribuicao_valores(df):
    """Gráfico de distribuição de valores"""
    if 'Total stake' not in df.columns:
        return None
        
    fig = px.box(
        df,
        y='Total stake',
        title="💰 Distribuição de Valores",
        points="all",
        color_discrete_sequence=['#FF9D9D']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#9D9DFF'
    )
    return fig


def grafico_top_ligas(df):
    """Gráfico das ligas mais apostadas"""
    if 'Bet champs' not in df.columns:
        return None
        
    top_ligas = df['Bet champs'].value_counts().head(5)
    
    fig = px.bar(
        x=top_ligas.values,
        y=top_ligas.index,
        orientation='h',
        title="🌏 Top 5 Ligas",
        color=top_ligas.values,
        color_continuous_scale=['#4B4BFF', '#9D4BFF']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#9D9DFF'
    )
    return fig
