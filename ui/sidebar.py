import streamlit as st
from copy import deepcopy
from ui.components.cards import tarjeta
from config.settings import DEFAULT_DATA
from infra.storage import guardar_datos, obtener_backend_activo


def render(data, r):
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 8px 0 16px 0;">
            <div style="font-size: 1.3rem; font-weight: 700;">📈 Estado Actual</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(tarjeta("CAPITAL", f"S/ {r['capital_total']:,.0f}", "#3b82f6", "💰"), unsafe_allow_html=True)
        st.markdown(tarjeta("GANANCIA TC", f"S/ {r['ganancia_tc']:,.2f}", "#10b981", "📊"), unsafe_allow_html=True)
        st.markdown(tarjeta("UTILIDAD BRUTA", f"US$ {r['utilidad_bruta']:,.0f}", "#8b5cf6", "🎯"), unsafe_allow_html=True)
        st.markdown(tarjeta("CUOTAS/MES", f"S/ {r['total_cuotas_mes']:,.0f}", "#f59e0b", "📅"), unsafe_allow_html=True)

        if data["meta"]["ultima_modificacion"]:
            st.caption(f"Ultima modificacion: {data['meta']['ultima_modificacion']}")

        st.markdown("---")
        if st.button("Resetear a datos base", type="secondary"):
            st.session_state.data = deepcopy(DEFAULT_DATA)
            guardar_datos(st.session_state.data)
            st.success("Datos reseteados.")
            st.rerun()

        st.markdown("---")
        st.caption(f"Persistencia activa: {obtener_backend_activo()}")
        st.caption("PWA: instala la app desde el menu del navegador en Chrome, Edge o Safari.")
