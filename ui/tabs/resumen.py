import streamlit as st
from ui.components.cards import tarjeta, seccion, flecha_flujo
from ui.components.charts import (
    chart_capital_bar, chart_cambio_barras, chart_gauge_devolucion,
    chart_fondo_disponible, chart_sankey, chart_waterfall_ventas,
)


def render(data, r):
    # ── Paso 1: Capital ──
    seccion("Origen del Capital", "1", "De donde sale el dinero")

    cols_cap = st.columns(len(data["origen_capital"]))
    for i, o in enumerate(data["origen_capital"]):
        es_prestamo = "prestamo" in o["tipo"].lower()
        color = "#ef4444" if es_prestamo else "#10b981"
        icono = "🏦" if es_prestamo else "👤"
        sub = f"Cuota: S/ {o['cuota']:,.0f}/mes" if o["cuota"] else "Sin cuotas"
        with cols_cap[i]:
            st.markdown(tarjeta(o["nombre"].upper(), f"S/ {o['monto']:,.0f}", color, icono, sub),
                        unsafe_allow_html=True)

    st.plotly_chart(chart_capital_bar(data), use_container_width=True)
    flecha_flujo()

    # ── Paso 2: Compra de USD ──
    seccion("Primera compra de dolares", "2",
            f"S/ {r['soles_usados']:,.0f} entran a dolares, S/ {r['soles_libres']:,.0f} quedan libres")

    p2a, p2b, p2c, p2d = st.columns(4)
    with p2a:
        st.markdown(tarjeta("SOLES INVERTIDOS", f"S/ {r['soles_usados']:,.0f}", "#3b82f6", "💵"), unsafe_allow_html=True)
    with p2b:
        st.markdown(tarjeta("USD COMPRADOS", f"US$ {r['usd_comprados']:,.0f}", "#06b6d4", "💲"), unsafe_allow_html=True)
    with p2c:
        st.markdown(tarjeta("SOLES AL VENDER", f"S/ {r['soles_al_vender']:,.2f}", "#8b5cf6", "💸"), unsafe_allow_html=True)
    with p2d:
        st.markdown(tarjeta("GANANCIA", f"S/ {r['ganancia_tc']:,.2f}", "#10b981", "✅"), unsafe_allow_html=True)

    st.plotly_chart(chart_cambio_barras(r), use_container_width=True)

    # Flujo visual
    st.markdown(f"""
    <div style="
        background: var(--secondary-background-color);
        border-radius: 12px; padding: 16px 24px; margin: 4px 0;
        display: flex; align-items: center; justify-content: center; gap: 16px;
        flex-wrap: wrap; font-size: 0.9rem;
    ">
        <span style="font-weight: 600;">S/ {r['soles_usados']:,.0f}</span>
        <span style="opacity: 0.5;">→ compra a</span>
        <span style="background: #3b82f6; color: white; padding: 4px 12px;
            border-radius: 20px; font-weight: 600;">{r['tc_compra']:.2f}</span>
        <span style="opacity: 0.5;">→</span>
        <span style="font-weight: 600;">US$ {r['usd_comprados']:,.0f}</span>
        <span style="opacity: 0.5;">→ venta a</span>
        <span style="background: #10b981; color: white; padding: 4px 12px;
            border-radius: 20px; font-weight: 600;">{r['tc_venta']:.2f}</span>
        <span style="opacity: 0.5;">→</span>
        <span style="font-weight: 600;">S/ {r['soles_al_vender']:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    flecha_flujo()

    # ── Paso 3: Devolucion ──
    seccion("Devolucion y fondo disponible", "3", "Lo que ya regreso y lo que se puede usar")

    p3a, p3b, p3c = st.columns(3)
    with p3a:
        st.markdown(tarjeta("DEVUELTO", f"S/ {r['monto_devuelto']:,.0f}", "#10b981", "✅",
                            f"De S/ {r['soles_al_vender']:,.0f}"), unsafe_allow_html=True)
    with p3b:
        st.markdown(tarjeta("PENDIENTE", f"S/ {r['pendiente_devolver']:,.0f}", "#f59e0b", "⏳",
                            "Aun no regresa"), unsafe_allow_html=True)
    with p3c:
        st.markdown(tarjeta("FONDO DISPONIBLE", f"S/ {r['fondo_disponible']:,.0f}", "#8b5cf6", "💰",
                            f"S/ {r['soles_libres']:,.0f} libres + S/ {r['monto_devuelto']:,.0f} devuelto"), unsafe_allow_html=True)

    st.plotly_chart(chart_gauge_devolucion(r), use_container_width=True)
    st.plotly_chart(chart_fondo_disponible(r), use_container_width=True)

    flecha_flujo()

    # ── Paso 4: MDF ──
    seccion("Compra de MDF", "4", f"Costo total: US$ {r['usd_mdf']:,.0f}")

    p4a, p4b, p4c = st.columns(3)
    with p4a:
        st.markdown(tarjeta("COSTO MDF", f"US$ {r['usd_mdf']:,.0f}", "#3b82f6", "📦"), unsafe_allow_html=True)
    with p4b:
        st.markdown(tarjeta("2DA COMPRA USD", f"US$ {r['usd_2da_exacto']:,.2f}", "#06b6d4", "💲",
                            f"Manual: US$ {r['usd_2da_manual']:,.0f}"), unsafe_allow_html=True)
    with p4c:
        st.markdown(tarjeta("USD FALTANTES", f"US$ {r['usd_faltantes_exacto']:,.2f}", "#ef4444", "⚠",
                            f"= S/ {r['soles_faltantes_exacto']:,.2f}"), unsafe_allow_html=True)

    flecha_flujo()

    # ── Paso 5: Venta final ──
    seccion("Venta final de melaminas", "5", "Resultado de toda la operacion")

    p5a, p5b, p5c = st.columns(3)
    with p5a:
        st.markdown(tarjeta("MELAMINAS", f"{r['melaminas']:,} uds", "#6366f1", "🏭",
                            f"@ US$ {r['precio_melamina']:.2f} c/u"), unsafe_allow_html=True)
    with p5b:
        st.markdown(tarjeta("VENTAS PROYECTADAS", f"US$ {r['ventas_finales']:,.0f}", "#3b82f6", "📈"), unsafe_allow_html=True)
    with p5c:
        color_util = "#10b981" if r['utilidad_bruta'] >= 0 else "#ef4444"
        st.markdown(tarjeta("UTILIDAD BRUTA", f"US$ {r['utilidad_bruta']:,.0f}", color_util, "🎯",
                            f"Margen: {(r['utilidad_bruta']/r['usd_mdf']*100) if r['usd_mdf'] else 0:.1f}%"), unsafe_allow_html=True)

    # ── Sankey ──
    seccion("Flujo completo del dinero", "📊", "Como se mueve el capital desde el origen hasta la venta final")
    st.plotly_chart(chart_sankey(r), use_container_width=True)

    # ── Waterfall ──
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    st.plotly_chart(chart_waterfall_ventas(r), use_container_width=True)
