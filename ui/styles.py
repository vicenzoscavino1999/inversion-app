import streamlit as st


def aplicar_estilos():
    """Inyecta CSS global compatible con dark/light mode."""
    st.markdown("""
    <style>
        .block-container { padding-top: 1rem; max-width: 1200px; }
        div[data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border-radius: 10px;
            padding: 14px 18px;
            border: 1px solid rgba(128,128,128,0.15);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: var(--secondary-background-color);
            border-radius: 10px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
        }
        .streamlit-expanderHeader {
            border-radius: 8px;
            font-weight: 500;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        div[data-testid="stAlert"] { border-radius: 10px; }
        section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Renderiza el header principal."""
    st.markdown("""
    <div style="text-align: center; padding: 16px 0 8px 0;">
        <div style="font-size: 2.2rem; font-weight: 800; letter-spacing: -1px;">
            📈 Control de Inversiones
        </div>
        <div style="font-size: 0.95rem; opacity: 0.6; margin-top: 4px;">
            Gestiona y simula tus inversiones paso a paso
        </div>
    </div>
    """, unsafe_allow_html=True)
