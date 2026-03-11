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
            font-family: 'Arial Black', sans-serif;
        }
        
        .metric-delta {
            color: #4CAF50;
            font-size: 14px;
            font-weight: 500;
        }
        
        .metric-delta-negative {
            color: #FF4B4B;
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Alertas com cores */
        .alert-critical {
            background: linear-gradient(135deg, #FF4B4B20 0%, #FF4B4B10 100%);
            border-left: 5px solid #FF4B4B;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            backdrop-filter: blur(5px);
        }
        
        .alert-high {
            background: linear-gradient(135deg, #FFA64B20 0%, #FFA64B10 100%);
            border-left: 5px solid #FFA64B;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .alert-medium {
            background: linear-gradient(135deg, #FFD70020 0%, #FFD70010 100%);
            border-left: 5px solid #FFD700;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .alert-low {
            background: linear-gradient(135deg, #4CAF5020 0%, #4CAF5010 100%);
            border-left: 5px solid #4CAF50;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        /* Títulos com gradiente */
        .gradient-title {
            background: linear-gradient(90deg, #9D9DFF, #FF9D9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            font-family: 'Arial Black', sans-serif;
        }
        
        .gradient-subtitle {
            background: linear-gradient(90deg, #9D9DFF, #9D4BFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        /* Botões personalizados */
        .stButton > button {
            background: linear-gradient(90deg, #4B4BFF, #9D4BFF);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s;
            width: 100%;
            border: 1px solid #6D6DFF;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 25px rgba(75,75,255,0.5);
            border: 1px solid #9D9DFF;
        }
        
        /* Expander personalizado */
        .streamlit-expanderHeader {
            background-color: #1E1E2E;
            border-radius: 10px;
            border: 1px solid #3D3D5C;
            color: #9D9DFF;
            font-weight: bold;
        }
        
        /* DataFrame personalizado */
        .dataframe {
            background-color: #1E1E2E !important;
            border-radius: 10px !important;
            border: 1px solid #3D3D5C !important;
        }
        
        /* Tabs personalizadas */
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
            font-weight: 500;
            border: 1px solid #3D3D5C;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #4B4BFF, #9D4BFF);
            color: white;
            border: none;
        }
        
        /* Sidebar personalizada */
        .css-1d391kg {
            background-color: #1E1E2E;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: white !important;
        }
        
        /* Texto */
        p, li {
            color: #CCCCCC !important;
        }
        
        /* Divisores */
        hr {
            background: linear-gradient(90deg, #4B4BFF, #9D4BFF, #4B4BFF);
            height: 2px;
            border: none;
        }
        
        /* Loading personalizado */
        .stSpinner > div {
            border-top-color: #9D9DFF !important;
        }
        
        /* Success/Info/Warning/Error boxes */
        .stSuccess {
            background-color: #1E4B2E !important;
            border-left-color: #4CAF50 !important;
            color: white !important;
        }
        
        .stInfo {
            background-color: #1E2E4B !important;
            border-left-color: #4B4BFF !important;
            color: white !important;
        }
        
        .stWarning {
            background-color: #4B3D1E !important;
            border-left-color: #FFA64B !important;
            color: white !important;
        }
        
        .stError {
            background-color: #4B1E1E !important;
            border-left-color: #FF4B4B !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# COMPONENTES VISUAIS REUTILIZÁVEIS
# ============================================

def titulo_principal():
    """Renderiza o título principal com gradiente"""
    st.markdown('<h1 class="gradient-title">🛡️ DeepRisk Professional</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #9D9DFF; margin-bottom: 30px;">Auditoria de Risco e Integridade em Apostas Esportivas</p>', unsafe_allow_html=True)

def card_metrica(titulo, valor, delta=None, icone="📊", negativo=False):
    """Cria um card de métrica profissional"""
    delta_class = "metric-delta-negative" if negativo else "metric-delta"
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{icone} {titulo}</div>
        <div class="metric-value">{valor}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def alerta(tipo, titulo, mensagem):
    """Renderiza alertas coloridos por severidade"""
    if tipo == "CRÍTICO":
        st.markdown(f"""
        <div class="alert-critical">
            <strong style="color: #FF4B4B; font-size: 18px;">🚨 {titulo}</strong><br>
            <span style="color: white;">{mensagem}</span>
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "ALTO":
        st.markdown(f"""
        <div class="alert-high">
            <strong style="color: #FFA64B; font-size: 18px;">⚠️ {titulo}</strong><br>
            <span style="color: white;">{mensagem}</span>
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "MÉDIO":
        st.markdown(f"""
        <div class="alert-medium">
            <strong style="color: #FFD700; font-size: 18px;">📌 {titulo}</strong><br>
            <span style="color: white;">{mensagem}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-low">
            <strong style="color: #4CAF50; font-size: 18px;">✅ {titulo}</strong><br>
            <span style="color: white;">{mensagem}</span>
        </div>
        """, unsafe_allow_html=True)

def sidebar_profissional():
    """Renderiza a sidebar com informações do sistema"""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1E1E2E/9D9DFF?text=DeepRisk", use_column_width=True)
        
        st.markdown("### 🎯 Configurações")
        
        sensibilidade = st.select_slider(
            "Sensibilidade",
            options=["Baixa", "Média", "Alta", "Crítica"],
            value="Média"
        )
        
        incluir_api = st.checkbox("🔍 Validar com The Odds API", value=True)
        
        st.markdown("---")
        st.markdown("### 📊 Status do Sistema")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Gemini:**")
            st.success("✅ Online")
        with col2:
            st.markdown("**Odds API:**")
            st.success("✅ Online")
        
        st.markdown("---")
        st.markdown("### ⏰ Última Análise")
        st.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return sensibilidade, incluir_api

def footer_profissional():
    """Renderiza o rodapé profissional"""
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**🛡️ DeepRisk v4.0**")
        st.caption("© 2026 - Todos direitos reservados")

    with col2:
        st.markdown("**📧 Suporte**")
        st.caption("suporte@deeprisk.com")

    with col3:
        st.markdown("**🔒 Segurança**")
        st.caption("ISO 27001 Certified")

    with col4:
        st.markdown("**📊 Versão**")
        st.caption("Enterprise Edition")

# ============================================
# GRÁFICOS PROFISSIONAIS
# ============================================

def grafico_distribuicao_horarios(df):
    """Gráfico de distribuição de apostas por horário"""
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
        title_font_color='#9D9DFF',
        showlegend=False
    )
    fig.update_xaxes(gridcolor='#3D3D5C')
    fig.update_yaxes(gridcolor='#3D3D5C')
    return fig

def grafico_distribuicao_valores(df):
    """Gráfico de distribuição de valores"""
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

def grafico_timeline_apostas(df):
    """Timeline de apostas interativa"""
    fig = px.scatter(
        df,
        x='Created date',
        y='Total stake',
        color='Bet status',
        size='Bet prices',
        hover_data=['Bet events'],
        title='📅 Timeline de Apostas',
        color_discrete_map={'Ganha': '#4CAF50', 'Perdida': '#FF4B4B'}
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#9D9DFF'
    )
    return fig

def grafico_pizza_riscos(metricas):
    """Gráfico de pizza para composição de riscos"""
    labels = ['Crítico', 'Alto', 'Médio', 'Baixo']
    values = [
        metricas.get('alertas_criticos', 0),
        metricas.get('alertas_altos', 0),
        metricas.get('alertas_medios', 0),
        metricas.get('alertas_baixos', 0)
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=['#FF4B4B', '#FFA64B', '#FFD700', '#4CAF50']
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#9D9DFF',
        title="⚖️ Composição de Riscos"
    )
    return fig

def grafico_top_ligas(df):
    """Gráfico das ligas mais apostadas"""
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
        title_font_color='#9D9DFF',
        xaxis_title="Quantidade",
        yaxis_title=""
    )
    return fig
