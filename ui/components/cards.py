import streamlit as st


def tarjeta(titulo, valor, color="#1f77b4", icono="", subtexto=""):
    """Genera una tarjeta HTML estilizada."""
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}22, {color}11);
        border-left: 4px solid {color};
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease;
    ">
        <div style="font-size: 0.8rem; opacity: 0.7; margin-bottom: 4px;">
            {icono} {titulo}
        </div>
        <div style="font-size: 1.6rem; font-weight: 700; letter-spacing: -0.5px;">
            {valor}
        </div>
        {f'<div style="font-size: 0.75rem; opacity: 0.6; margin-top: 4px;">{subtexto}</div>' if subtexto else ''}
    </div>
    """


def seccion(titulo, numero, descripcion=""):
    """Header de seccion con numero de paso."""
    st.markdown(f"""
    <div style="
        display: flex; align-items: center; gap: 12px;
        margin: 28px 0 16px 0;
    ">
        <div style="
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border-radius: 50%;
            width: 36px; height: 36px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 1rem;
            flex-shrink: 0;
        ">{numero}</div>
        <div>
            <div style="font-size: 1.15rem; font-weight: 600;">{titulo}</div>
            {f'<div style="font-size: 0.8rem; opacity: 0.6;">{descripcion}</div>' if descripcion else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def flecha_flujo():
    """Flecha visual entre pasos."""
    st.markdown("""
    <div style="text-align: center; margin: 8px 0; opacity: 0.4; font-size: 1.4rem;">
        ⬇
    </div>
    """, unsafe_allow_html=True)
