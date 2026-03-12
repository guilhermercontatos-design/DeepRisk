# layout/componentes.py
import streamlit as st

def card_metrica(titulo, valor, delta=None, icone="📊"):
    """Cria um card de métrica"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{icone} {titulo}</div>
        <div class="metric-value">{valor}</div>
        {f'<div style="color: #4CAF50;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def alerta_componente(severidade, titulo, descricao, evidencias):
    """Renderiza alerta formatado"""
    cores = {
        'CRÍTICO': '#FF4B4B',
        'ALTO': '#FFA64B',
        'MÉDIO': '#FFD700',
        'BAIXO': '#4CAF50'
    }
    cor = cores.get(severidade, '#FFD700')
    
    st.markdown(f"""
    <div style="background: {cor}20; border-left: 5px solid {cor}; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <strong style="color: {cor};">{titulo}</strong><br>
        <span style="color: white;">{descricao}</span>
    </div>
    """, unsafe_allow_html=True)

def footer_profissional():
    """Renderiza rodapé"""
    st.markdown("---")
    st.markdown("**🛡️ DeepRisk Ultimate v4.0**")
    st.caption("© 2026 - Todos direitos reservados")
