# layout/estilos.py
import streamlit as st

def aplicar_tema_profissional():
    """Aplica o CSS personalizado"""
    st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
        }
        .metric-card {
            background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #3D3D5C;
            margin: 10px 0;
        }
        .metric-title {
            color: #9D9DFF;
            font-size: 14px;
            text-transform: uppercase;
        }
        .metric-value {
            color: white;
            font-size: 32px;
            font-weight: bold;
        }
        .stButton > button {
            background: linear-gradient(90deg, #4B4BFF, #9D4BFF);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: bold;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 25px rgba(75,75,255,0.5);
        }
    </style>
    """, unsafe_allow_html=True)
