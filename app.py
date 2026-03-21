import streamlit as st
from config.settings import PAGE_CONFIG
from core.storage import cargar_datos
from core.calculadora import calcular_todo
from ui.styles import aplicar_estilos, render_header
from ui.components.cards import tarjeta
from ui.sidebar import render as render_sidebar
from ui.tabs import resumen, capital, cambio, mdf_venta, simulador, historial

# ─── Page config ───
st.set_page_config(**PAGE_CONFIG)

# ─── Cargar datos ───
if "data" not in st.session_state:
    st.session_state.data = cargar_datos()

data = st.session_state.data
r = calcular_todo(data)

# ─── Estilos y header ───
aplicar_estilos()
render_header()

# ─── Resumen rapido (tarjetas superiores) ───
st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(tarjeta("CAPITAL TOTAL", f"S/ {r['capital_total']:,.0f}", "#3b82f6", "💰",
                         f"{len(data['origen_capital'])} fuentes"), unsafe_allow_html=True)
with c2:
    color_g = "#10b981" if r['ganancia_tc'] >= 0 else "#ef4444"
    st.markdown(tarjeta("GANANCIA TC", f"S/ {r['ganancia_tc']:,.2f}", color_g, "📊",
                         f"Spread: {r['tc_venta'] - r['tc_compra']:.4f}"), unsafe_allow_html=True)
with c3:
    st.markdown(tarjeta("FONDO DISPONIBLE", f"S/ {r['fondo_disponible']:,.0f}", "#8b5cf6", "🏦",
                         f"Libre + Devuelto"), unsafe_allow_html=True)
with c4:
    color_u = "#10b981" if r['utilidad_bruta'] >= 0 else "#ef4444"
    st.markdown(tarjeta("UTILIDAD BRUTA", f"US$ {r['utilidad_bruta']:,.0f}", color_u, "🎯",
                         f"{r['melaminas']:,} melaminas"), unsafe_allow_html=True)
with c5:
    st.markdown(tarjeta("CUOTAS / MES", f"S/ {r['total_cuotas_mes']:,.0f}", "#f59e0b", "📅",
                         f"Compromisos fijos"), unsafe_allow_html=True)

st.markdown("<div style='height: 4px'></div>", unsafe_allow_html=True)

# ─── Tabs ───
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "  Resumen  ",
    "  Capital  ",
    "  Cambio  ",
    "  MDF y Venta  ",
    "  Simulador  ",
    "  Historial  ",
])

with tab1:
    resumen.render(data, r)

with tab2:
    capital.render(data, r)

with tab3:
    cambio.render(data)

with tab4:
    mdf_venta.render(data)

with tab5:
    simulador.render(data)

with tab6:
    historial.render(data, r)

# ─── Sidebar ───
render_sidebar(data, r)
