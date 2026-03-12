# layout/componentes.py - VERSÃO SÓBRIA
import streamlit as st

def titulo_principal(titulo, subtitulo):
    """Título corporativo elegante"""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 class="main-title">{titulo}</h1>
        <p class="main-subtitle">{subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)

def card_metrica(titulo, valor, delta=None, icone="📊", negativo=False):
    """Card de métrica corporativo"""
    delta_class = "metric-delta-negative" if negativo else "metric-delta"
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{icone} {titulo}</div>
        <div class="metric-value">{valor}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def alerta_componente(severidade, titulo, descricao, evidencias):
    """Alerta corporativo"""
    
    if severidade == "CRÍTICO":
        st.markdown(f"""
        <div class="alert-critical">
            <strong style="color: #C0392B; font-size: 16px;">🚨 {titulo}</strong><br>
            <span style="color: #2C3E50;">{descricao}</span>
        </div>
        """, unsafe_allow_html=True)
    elif severidade == "ALTO":
        st.markdown(f"""
        <div class="alert-high">
            <strong style="color: #E67E22; font-size: 16px;">⚠️ {titulo}</strong><br>
            <span style="color: #2C3E50;">{descricao}</span>
        </div>
        """, unsafe_allow_html=True)
    elif sever
