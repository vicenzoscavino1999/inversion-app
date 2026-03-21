import streamlit as st
from copy import deepcopy
from ui.components.cards import seccion
from ui.components.charts import chart_simulador_barras, chart_radar
from core.calculadora import calcular_todo


def render(data):
    seccion("Simulador", "🧮", "Proba escenarios sin afectar los datos reales")

    sim_data = deepcopy(data)

    st.markdown("##### Capital adicional")
    sim_capital_extra = st.number_input("Capital adicional (S/)", value=0.0, step=500.0, key="sim_cap",
                                         help="Agrega capital simulado para ver como cambian los numeros")
    if sim_capital_extra:
        sim_data["origen_capital"].append({
            "nombre": "Capital simulado", "tipo": "Capital personal",
            "monto": sim_capital_extra, "cuota": 0, "plazo": 0, "comentario": "Simulacion"
        })

    st.markdown("##### Tipo de cambio")
    sim1, sim2 = st.columns(2)
    sim_tc_c = sim1.number_input("TC Compra simulado", value=float(data["operaciones_cambio"][0]["tc_compra"]),
                                  step=0.01, format="%.4f", key="sim_tcc")
    sim_tc_v = sim2.number_input("TC Venta simulado", value=float(data["operaciones_cambio"][0]["tc_venta"]),
                                  step=0.01, format="%.4f", key="sim_tcv")
    sim_data["operaciones_cambio"][0]["tc_compra"] = sim_tc_c
    sim_data["operaciones_cambio"][0]["tc_venta"] = sim_tc_v

    st.markdown("##### Venta de melaminas")
    sim3, sim4 = st.columns(2)
    sim_mel = sim3.number_input("Melaminas (sim)", value=int(data["venta_final"]["melaminas"]),
                                 step=10, key="sim_mel")
    sim_precio = sim4.number_input("Precio/unidad (sim)", value=float(data["venta_final"]["precio_por_unidad"]),
                                    step=0.10, format="%.2f", key="sim_precio")
    sim_data["venta_final"]["melaminas"] = sim_mel
    sim_data["venta_final"]["precio_por_unidad"] = sim_precio

    r_sim = calcular_todo(sim_data)
    r_real = calcular_todo(data)

    st.markdown("---")
    st.markdown("##### Real vs Simulado")

    comparaciones = [
        ("Capital Total", r_real["capital_total"], r_sim["capital_total"], "S/", "#3b82f6"),
        ("Ganancia TC", r_real["ganancia_tc"], r_sim["ganancia_tc"], "S/", "#10b981"),
        ("USD comprados", r_real["usd_comprados"], r_sim["usd_comprados"], "US$", "#06b6d4"),
        ("Ventas finales", r_real["ventas_finales"], r_sim["ventas_finales"], "US$", "#8b5cf6"),
        ("Utilidad bruta", r_real["utilidad_bruta"], r_sim["utilidad_bruta"], "US$", "#f59e0b"),
    ]

    cols = st.columns(5)
    for i, (label, real, sim, moneda, color) in enumerate(comparaciones):
        delta = sim - real
        signo = "+" if delta > 0 else ""
        delta_txt = f"{signo}{moneda} {delta:,.2f}" if delta != 0 else "Sin cambio"
        delta_color = "#10b981" if delta > 0 else "#ef4444" if delta < 0 else "#888"
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}22, {color}11);
                border-left: 4px solid {color};
                border-radius: 10px; padding: 16px; margin-bottom: 8px;
            ">
                <div style="font-size: 0.75rem; opacity: 0.6;">{label}</div>
                <div style="font-size: 1.3rem; font-weight: 700;">{moneda} {sim:,.2f}</div>
                <div style="font-size: 0.8rem; color: {delta_color}; font-weight: 600; margin-top: 4px;">
                    {delta_txt}
                </div>
                <div style="font-size: 0.7rem; opacity: 0.5;">Real: {moneda} {real:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Grafico comparativo")

    vals_real = [c[1] for c in comparaciones]
    vals_sim = [c[2] for c in comparaciones]

    st.plotly_chart(chart_simulador_barras(comparaciones, vals_real, vals_sim), use_container_width=True)
    st.plotly_chart(chart_radar(vals_real, vals_sim), use_container_width=True)
