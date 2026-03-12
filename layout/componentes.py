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
    elif severidade == "MÉDIO":
        st.markdown(f"""
        <div class="alert-medium">
            <strong style="color: #F1C40F; font-size: 16px;">📌 {titulo}</strong><br>
            <span style="color: #2C3E50;">{descricao}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-low">
            <strong style="color: #27AE60; font-size: 16px;">✅ {titulo}</strong><br>
            <span style="color: #2C3E50;">{descricao}</span>
        </div>
        """, unsafe_allow_html=True)

def footer_profissional():
    """Rodapé corporativo"""
    st.markdown("""
    <div class="footer">
        <p style="margin: 0;">© 2026 DeepRisk - Auditoria de Integridade em Apostas Esportivas</p>
        <p style="margin: 5px 0 0 0; font-size: 11px;">Versão 4.0 - Todos os direitos reservados</p>
    </div>
    """, unsafe_allow_html=True)

def card_info(titulo, valor):
    """Card de informação simples"""
    st.markdown(f"""
    <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #E0E4E8; margin: 5px 0;">
        <div style="color: #5D6D7E; font-size: 12px;">{titulo}</div>
        <div style="color: #1A2B3C; font-size: 18px; font-weight: 600;">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

def linha_divisoria():
    """Linha divisória elegante"""
    st.markdown("""
    <div style="margin: 30px 0; border-bottom: 1px solid #E0E4E8;"></div>
    """, unsafe_allow_html=True)
