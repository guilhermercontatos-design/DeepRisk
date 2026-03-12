# layout/estilos.py - VERSÃO SÓBRIA E PROFISSIONAL
import streamlit as st

def aplicar_tema_profissional():
    """Aplica o CSS corporativo - Sóbrio e Profissional"""
    
    st.markdown("""
    <style>
        /* Tema corporativo - tons de cinza e azul marinho */
        .stApp {
            background-color: #F5F7FA;
        }
        
        /* Cards elegantes */
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #E0E4E8;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            margin: 10px 0;
            transition: all 0.2s;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-color: #2C3E50;
        }
        
        .metric-title {
            color: #5D6D7E;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        
        .metric-value {
            color: #1A2B3C;
            font-size: 28px;
            font-weight: 600;
            margin: 5px 0;
            font-family: 'Inter', sans-serif;
        }
        
        .metric-delta {
            color: #27AE60;
            font-size: 13px;
            font-weight: 500;
        }
        
        .metric-delta-negative {
            color: #E74C3C;
            font-size: 13px;
            font-weight: 500;
        }
        
        /* Alertas corporativos */
        .alert-critical {
            background: #FEF5F5;
            border-left: 4px solid #C0392B;
            padding: 16px;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        .alert-high {
            background: #FEF9E7;
            border-left: 4px solid #E67E22;
            padding: 16px;
            border-radius: 6px;
        }
        
        .alert-medium {
            background: #F8F9F9;
            border-left: 4px solid #F1C40F;
            padding: 16px;
            border-radius: 6px;
        }
        
        .alert-low {
            background: #F5F8F5;
            border-left: 4px solid #27AE60;
            padding: 16px;
            border-radius: 6px;
        }
        
        /* Título principal */
        .main-title {
            color: #1A2B3C;
            font-size: 36px;
            font-weight: 600;
            text-align: center;
            margin: 20px 0 5px 0;
            font-family: 'Inter', sans-serif;
        }
        
        .main-subtitle {
            color: #5D6D7E;
            font-size: 16px;
            text-align: center;
            margin-bottom: 40px;
            font-weight: 400;
        }
        
        /* Botões corporativos */
        .stButton > button {
            background: #2C3E50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 30px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s;
            width: 100%;
            border: 1px solid #2C3E50;
        }
        
        .stButton > button:hover {
            background: #1A2B3C;
            border: 1px solid #1A2B3C;
            box-shadow: 0 4px 12px rgba(44,62,80,0.15);
        }
        
        /* Tabs elegantes */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: white;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid #E0E4E8;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 8px 20px;
            background: transparent;
            color: #5D6D7E;
            font-weight: 500;
            border: none;
        }
        
        .stTabs [aria-selected="true"] {
            background: #2C3E50;
            color: white;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #1A2B3C !important;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        
        h2 {
            font-size: 24px;
            border-bottom: 2px solid #E0E4E8;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        
        h3 {
            font-size: 18px;
            color: #2C3E50 !important;
        }
        
        /* Texto */
        p, li {
            color: #2C3E50 !important;
            font-size: 14px;
            line-height: 1.6;
        }
        
        /* Divisores */
        hr {
            background: #E0E4E8;
            height: 1px;
            border: none;
            margin: 30px 0;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: white;
            border-right: 1px solid #E0E4E8;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: white;
            border: 1px solid #E0E4E8;
            border-radius: 6px;
            color: #2C3E50;
            font-weight: 500;
        }
        
        /* DataFrames */
        .dataframe {
            border: 1px solid #E0E4E8 !important;
            border-radius: 6px !important;
        }
        
        /* Success/Info/Warning/Error boxes */
        .stSuccess {
            background: #E8F5E9 !important;
            border-left-color: #27AE60 !important;
            color: #1A2B3C !important;
        }
        
        .stInfo {
            background: #E3F2FD !important;
            border-left-color: #3498DB !important;
            color: #1A2B3C !important;
        }
        
        .stWarning {
            background: #FFF3E0 !important;
            border-left-color: #F39C12 !important;
            color: #1A2B3C !important;
        }
        
        .stError {
            background: #FDECEA !important;
            border-left-color: #E74C3C !important;
            color: #1A2B3C !important;
        }
        
        /* Footer */
        .footer {
            color: #5D6D7E;
            font-size: 12px;
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #E0E4E8;
        }
    </style>
    """, unsafe_allow_html=True)
