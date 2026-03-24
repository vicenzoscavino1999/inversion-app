import streamlit as st
from datetime import datetime
from ui.components.cards import tarjeta, seccion
from infra.storage import guardar_datos


def render(data, r):
    seccion("Historial de cambios", "📜", "Guarda snapshots para comparar en el tiempo")

    col_snap1, col_snap2 = st.columns([3, 1])
    nota_snap = col_snap1.text_input("Nota para el snapshot (opcional)", key="nota_snapshot",
                                      placeholder="Ej: Actualizado TC despues de cotizacion...")
    with col_snap2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("Guardar snapshot", key="snapshot", type="primary"):
            snapshot = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "capital_total": r["capital_total"],
                "ganancia_tc": r["ganancia_tc"],
                "utilidad_bruta": r["utilidad_bruta"],
                "ventas_finales": r["ventas_finales"],
                "fondo_disponible": r["fondo_disponible"],
                "nota": st.session_state.get("nota_snapshot", ""),
            }
            data["historial"].append(snapshot)
            guardar_datos(data)
            st.success("Snapshot guardado.")
            st.rerun()

    if data["historial"]:
        st.markdown("---")
        for i, h in enumerate(reversed(data["historial"])):
            idx = len(data["historial"]) - 1 - i
            with st.expander(f"📌 {h['fecha']}  —  Capital: S/ {h['capital_total']:,.0f}  |  Utilidad: US$ {h['utilidad_bruta']:,.0f}"):
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    st.markdown(tarjeta("CAPITAL", f"S/ {h['capital_total']:,.0f}", "#3b82f6", "💰"), unsafe_allow_html=True)
                with hc2:
                    st.markdown(tarjeta("GANANCIA TC", f"S/ {h['ganancia_tc']:,.2f}", "#10b981", "📊"), unsafe_allow_html=True)
                with hc3:
                    st.markdown(tarjeta("UTILIDAD", f"US$ {h['utilidad_bruta']:,.0f}", "#8b5cf6", "🎯"), unsafe_allow_html=True)
                if h.get("nota"):
                    st.info(f"📝 {h['nota']}")
                if st.button(f"Eliminar este snapshot", key=f"del_hist_{idx}", type="secondary"):
                    data["historial"].pop(idx)
                    guardar_datos(data)
                    st.rerun()
    else:
        st.info("No hay snapshots todavia. Usa el boton de arriba para guardar el estado actual.")
