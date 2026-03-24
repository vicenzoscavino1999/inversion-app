import streamlit as st
from ui.components.cards import tarjeta, seccion
from ui.components.charts import chart_mdf_waterfall, chart_gauge_margen_melaminas, chart_costo_vs_venta
from core.calculadora import calcular_todo
from infra.storage import guardar_datos


def render(data):
    seccion("Compra de MDF y Venta Final", "📦", "Material y venta de melaminas")

    cambios_mdf = False

    st.markdown("##### Compra de MDF")
    m1, m2 = st.columns(2)
    new_usd_mdf = m1.number_input("USD total del MDF", value=float(data["mdf"]["usd_total"]),
                                   step=100.0, key="usd_mdf")
    new_soles_falt = m2.number_input("Soles faltantes (manual)", value=float(data["mdf"]["soles_faltantes_manual"]),
                                      step=100.0, key="soles_falt")
    if new_usd_mdf != data["mdf"]["usd_total"] or new_soles_falt != data["mdf"]["soles_faltantes_manual"]:
        data["mdf"]["usd_total"] = new_usd_mdf
        data["mdf"]["soles_faltantes_manual"] = new_soles_falt
        cambios_mdf = True

    st.markdown("##### Venta de Melaminas")
    v1, v2 = st.columns(2)
    new_mel = v1.number_input("Cantidad de melaminas", value=int(data["venta_final"]["melaminas"]),
                               step=10, key="melaminas")
    new_precio = v2.number_input("Precio por unidad (USD)", value=float(data["venta_final"]["precio_por_unidad"]),
                                  step=0.10, format="%.2f", key="precio_mel")
    if new_mel != data["venta_final"]["melaminas"] or new_precio != data["venta_final"]["precio_por_unidad"]:
        data["venta_final"]["melaminas"] = new_mel
        data["venta_final"]["precio_por_unidad"] = new_precio
        cambios_mdf = True

    r_temp = calcular_todo(data)

    st.markdown("---")
    st.markdown("##### Resultados calculados")

    rm1, rm2, rm3 = st.columns(3)
    with rm1:
        st.markdown(tarjeta("USD FALTANTES", f"US$ {r_temp['usd_faltantes_exacto']:,.2f}", "#ef4444", "⚠"), unsafe_allow_html=True)
    with rm2:
        st.markdown(tarjeta("VENTAS PROYECTADAS", f"US$ {r_temp['ventas_finales']:,.0f}", "#3b82f6", "📈"), unsafe_allow_html=True)
    with rm3:
        color_u = "#10b981" if r_temp['utilidad_bruta'] >= 0 else "#ef4444"
        margen = (r_temp['utilidad_bruta'] / r_temp['usd_mdf'] * 100) if r_temp['usd_mdf'] else 0
        st.markdown(tarjeta("UTILIDAD BRUTA", f"US$ {r_temp['utilidad_bruta']:,.0f}", color_u, "🎯",
                            f"Margen: {margen:.1f}%"), unsafe_allow_html=True)

    rm4, rm5 = st.columns(2)
    with rm4:
        st.markdown(tarjeta("PENDIENTE (MANUAL)", f"S/ {r_temp['pendiente_manual']:,.2f}", "#f59e0b", "⏳"), unsafe_allow_html=True)
    with rm5:
        st.markdown(tarjeta("LIBERADO/DEVUELTO", f"S/ {r_temp['total_liberado_manual']:,.0f}", "#10b981", "✅"), unsafe_allow_html=True)

    # Graficos
    st.markdown("---")
    st.markdown("##### Visualizacion de costos y ganancias")

    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        st.plotly_chart(chart_mdf_waterfall(r_temp), use_container_width=True)
    with fig_col2:
        st.plotly_chart(chart_gauge_margen_melaminas(r_temp), use_container_width=True)

    st.plotly_chart(chart_costo_vs_venta(r_temp), use_container_width=True)

    if cambios_mdf:
        if st.button("Guardar cambios en MDF/Venta", type="primary", key="save_mdf"):
            guardar_datos(data)
            st.success("Cambios guardados.")
            st.rerun()
