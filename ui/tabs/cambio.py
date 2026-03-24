import streamlit as st
from ui.components.cards import tarjeta, seccion
from ui.components.charts import chart_op_soles, chart_gauge_rentabilidad, chart_dona_devolucion
from core.calculadora import calcular_todo
from infra.storage import guardar_datos


def render(data):
    seccion("Operacion Cambiaria", "🔄", "Compra y venta de dolares")

    cambios_op = False

    st.markdown("##### Primera compra de dolares")
    if data["operaciones_cambio"]:
        op = data["operaciones_cambio"][0]
        oc1, oc2, oc3 = st.columns(3)
        new_soles = oc1.number_input("Soles usados", value=float(op["soles_usados"]), step=100.0, key="op_soles")
        new_tc_c = oc2.number_input("TC Compra", value=float(op["tc_compra"]), step=0.01, format="%.4f", key="op_tcc")
        new_tc_v = oc3.number_input("TC Venta", value=float(op["tc_venta"]), step=0.01, format="%.4f", key="op_tcv")

        if (new_soles != op["soles_usados"] or new_tc_c != op["tc_compra"] or new_tc_v != op["tc_venta"]):
            data["operaciones_cambio"][0]["soles_usados"] = new_soles
            data["operaciones_cambio"][0]["tc_compra"] = new_tc_c
            data["operaciones_cambio"][0]["tc_venta"] = new_tc_v
            cambios_op = True

    st.markdown("##### Devolucion")
    new_devuelto = st.number_input("Monto devuelto (S/)", value=float(data["devolucion"]["monto_devuelto"]),
                                    step=500.0, key="devuelto")
    if new_devuelto != data["devolucion"]["monto_devuelto"]:
        data["devolucion"]["monto_devuelto"] = new_devuelto
        cambios_op = True

    st.markdown("##### Segunda compra de dolares")
    sc1, sc2 = st.columns(2)
    new_usd_man = sc1.number_input("USD manual (apunte)", value=float(data["segunda_compra"]["usd_manual"]),
                                    step=100.0, key="usd_man")
    new_tc2 = sc2.number_input("TC segunda compra", value=float(data["segunda_compra"]["tc"]),
                                step=0.01, format="%.4f", key="tc2")
    if new_usd_man != data["segunda_compra"]["usd_manual"] or new_tc2 != data["segunda_compra"]["tc"]:
        data["segunda_compra"]["usd_manual"] = new_usd_man
        data["segunda_compra"]["tc"] = new_tc2
        cambios_op = True

    r_temp = calcular_todo(data)

    st.markdown("---")
    st.markdown("##### Resultados calculados")

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.markdown(tarjeta("USD COMPRADOS (1RA)", f"US$ {r_temp['usd_comprados']:,.0f}", "#06b6d4", "💲"), unsafe_allow_html=True)
    with rc2:
        st.markdown(tarjeta("SOLES AL VENDER", f"S/ {r_temp['soles_al_vender']:,.2f}", "#8b5cf6", "💸"), unsafe_allow_html=True)
    with rc3:
        st.markdown(tarjeta("GANANCIA TC", f"S/ {r_temp['ganancia_tc']:,.2f}", "#10b981", "✅"), unsafe_allow_html=True)

    rc4, rc5, rc6 = st.columns(3)
    with rc4:
        st.markdown(tarjeta("FONDO DISPONIBLE", f"S/ {r_temp['fondo_disponible']:,.0f}", "#8b5cf6", "💰"), unsafe_allow_html=True)
    with rc5:
        st.markdown(tarjeta("USD 2DA EXACTO", f"US$ {r_temp['usd_2da_exacto']:,.2f}", "#06b6d4", "🔢"), unsafe_allow_html=True)
    with rc6:
        color_diff = "#f59e0b" if abs(r_temp['diferencia_2da']) > 1 else "#10b981"
        st.markdown(tarjeta("DIFERENCIA", f"US$ {r_temp['diferencia_2da']:,.2f}", color_diff, "⚖",
                            "Manual vs exacto"), unsafe_allow_html=True)

    # Graficos
    st.markdown("---")
    st.markdown("##### Visualizacion de la operacion")

    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        st.plotly_chart(chart_op_soles(r_temp), use_container_width=True)
    with fig_col2:
        st.plotly_chart(chart_gauge_rentabilidad(r_temp), use_container_width=True)

    st.plotly_chart(chart_dona_devolucion(r_temp), use_container_width=True)

    if cambios_op:
        if st.button("Guardar cambios en operacion", type="primary", key="save_op"):
            guardar_datos(data)
            st.success("Cambios guardados.")
            st.rerun()
