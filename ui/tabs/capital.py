import streamlit as st
from ui.components.cards import seccion
from ui.components.charts import chart_dona_capital
from core.storage import guardar_datos


def render(data, r):
    seccion("Origen del Capital", "💵", "Edita los montos o agrega nuevas fuentes")

    st.plotly_chart(chart_dona_capital(data, r["capital_total"]), use_container_width=True)
    st.markdown("---")

    cambios_capital = False

    for i, origen in enumerate(data["origen_capital"]):
        es_prestamo = "prestamo" in origen["tipo"].lower()
        icono = "🏦" if es_prestamo else "👤"
        color_tag = "red" if es_prestamo else "green"

        with st.expander(f"{icono} {origen['nombre']}  —  S/ {origen['monto']:,.2f}  :{color_tag}[{origen['tipo']}]", expanded=False):
            col_a, col_b = st.columns(2)
            nuevo_nombre = col_a.text_input("Nombre", origen["nombre"], key=f"cap_nom_{i}")
            nuevo_tipo = col_b.selectbox("Tipo", ["Capital personal", "Prestamo"],
                                          index=0 if "personal" in origen["tipo"].lower() else 1,
                                          key=f"cap_tipo_{i}")
            col_c, col_d, col_e = st.columns(3)
            nuevo_monto = col_c.number_input("Monto (S/)", value=float(origen["monto"]), step=100.0, key=f"cap_monto_{i}")
            nueva_cuota = col_d.number_input("Cuota mensual (S/)", value=float(origen["cuota"]), step=50.0, key=f"cap_cuota_{i}")
            nuevo_plazo = col_e.number_input("Plazo (meses)", value=int(origen["plazo"]), step=1, key=f"cap_plazo_{i}")
            nuevo_comentario = st.text_input("Comentario", origen["comentario"], key=f"cap_com_{i}")

            if (nuevo_nombre != origen["nombre"] or nuevo_tipo != origen["tipo"] or
                nuevo_monto != origen["monto"] or nueva_cuota != origen["cuota"] or
                nuevo_plazo != origen["plazo"] or nuevo_comentario != origen["comentario"]):
                data["origen_capital"][i] = {
                    "nombre": nuevo_nombre, "tipo": nuevo_tipo, "monto": nuevo_monto,
                    "cuota": nueva_cuota, "plazo": nuevo_plazo, "comentario": nuevo_comentario,
                }
                cambios_capital = True

            if st.button(f"Eliminar {origen['nombre']}", key=f"del_cap_{i}", type="secondary"):
                data["origen_capital"].pop(i)
                guardar_datos(data)
                st.rerun()

    st.markdown("---")
    st.markdown("##### Agregar nueva fuente")
    with st.form("nuevo_capital", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        nc_nombre = fc1.text_input("Nombre")
        nc_tipo = fc2.selectbox("Tipo", ["Capital personal", "Prestamo"])
        fc3, fc4, fc5 = st.columns(3)
        nc_monto = fc3.number_input("Monto (S/)", value=0.0, step=100.0)
        nc_cuota = fc4.number_input("Cuota mensual", value=0.0, step=50.0)
        nc_plazo = fc5.number_input("Plazo (meses)", value=0, step=1)
        nc_comentario = st.text_input("Comentario")

        if st.form_submit_button("Agregar fuente de capital", type="primary"):
            if nc_nombre and nc_monto > 0:
                data["origen_capital"].append({
                    "nombre": nc_nombre, "tipo": nc_tipo, "monto": nc_monto,
                    "cuota": nc_cuota, "plazo": nc_plazo, "comentario": nc_comentario,
                })
                guardar_datos(data)
                st.success(f"Se agrego {nc_nombre} por S/ {nc_monto:,.2f}")
                st.rerun()
            else:
                st.warning("Completa nombre y monto.")

    if cambios_capital:
        if st.button("Guardar cambios en capital", type="primary"):
            guardar_datos(data)
            st.success("Cambios guardados.")
            st.rerun()
