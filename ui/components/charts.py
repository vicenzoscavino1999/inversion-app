import plotly.graph_objects as go


CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


def chart_capital_bar(data):
    """Barra horizontal stacked de composicion del capital."""
    fig = go.Figure()
    for o in data["origen_capital"]:
        es_p = "prestamo" in o["tipo"].lower()
        fig.add_trace(go.Bar(
            y=["Capital"], x=[o["monto"]], name=o["nombre"],
            orientation="h",
            marker_color="#ef4444" if es_p else "#10b981",
            text=f"{o['nombre']}: S/ {o['monto']:,.0f}",
            textposition="inside", textfont=dict(color="white", size=12),
            hovertemplate=f"<b>{o['nombre']}</b><br>S/ {o['monto']:,.0f}<br>{o['tipo']}<extra></extra>",
        ))
    fig.update_layout(
        **CHART_LAYOUT, barmode="stack", height=80,
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig


def chart_cambio_barras(r):
    """Barras comparativas: soles invertidos vs soles al vender vs ganancia."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Soles invertidos", "Soles al vender", "Ganancia"],
        y=[r["soles_usados"], r["soles_al_vender"], r["ganancia_tc"]],
        marker_color=["#3b82f6", "#8b5cf6", "#10b981"],
        text=[f"S/ {r['soles_usados']:,.0f}", f"S/ {r['soles_al_vender']:,.2f}", f"S/ {r['ganancia_tc']:,.2f}"],
        textposition="outside", textfont=dict(size=13),
        hovertemplate="%{x}<br><b>%{text}</b><extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT, height=300,
        margin=dict(t=20, b=40, l=40, r=20),
        showlegend=False, yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    return fig


def chart_gauge_devolucion(r):
    """Gauge de % devuelto de la 1ra venta."""
    pct = (r["monto_devuelto"] / r["soles_al_vender"] * 100) if r["soles_al_vender"] else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%", "font": {"size": 36}},
        delta={"reference": 100, "suffix": "%", "increasing": {"color": "#10b981"}},
        title={"text": "Porcentaje devuelto de la 1ra venta", "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": "#10b981"},
            "bgcolor": "rgba(128,128,128,0.1)",
            "steps": [
                {"range": [0, 33], "color": "rgba(239,68,68,0.15)"},
                {"range": [33, 66], "color": "rgba(245,158,11,0.15)"},
                {"range": [66, 100], "color": "rgba(16,185,129,0.15)"},
            ],
        }
    ))
    fig.update_layout(**CHART_LAYOUT, height=250, margin=dict(t=40, b=20, l=40, r=40))
    return fig


def chart_fondo_disponible(r):
    """Barra stacked: composicion del fondo disponible."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Fondo disponible"], x=[r["soles_libres"]], name="Soles libres",
        orientation="h", marker_color="#3b82f6",
        text=f"Libres: S/ {r['soles_libres']:,.0f}", textposition="inside",
        textfont=dict(color="white", size=12),
    ))
    fig.add_trace(go.Bar(
        y=["Fondo disponible"], x=[r["monto_devuelto"]], name="Devuelto",
        orientation="h", marker_color="#10b981",
        text=f"Devuelto: S/ {r['monto_devuelto']:,.0f}", textposition="inside",
        textfont=dict(color="white", size=12),
    ))
    fig.update_layout(
        **CHART_LAYOUT, barmode="stack", height=70,
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=True, legend=dict(orientation="h", y=-0.3),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig


def chart_sankey(r):
    """Diagrama Sankey del flujo completo del dinero."""
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20, thickness=25,
            label=[
                f"Capital Total\nS/ {r['capital_total']:,.0f}",
                f"Compra USD\nS/ {r['soles_usados']:,.0f}",
                f"Soles libres\nS/ {r['soles_libres']:,.0f}",
                f"USD 1ra\nUS$ {r['usd_comprados']:,.0f}",
                f"Venta USD\nS/ {r['soles_al_vender']:,.0f}",
                f"Devuelto\nS/ {r['monto_devuelto']:,.0f}",
                f"Pendiente\nS/ {r['pendiente_devolver']:,.0f}",
                f"Fondo disp.\nS/ {r['fondo_disponible']:,.0f}",
                f"USD 2da\nUS$ {r['usd_2da_exacto']:,.0f}",
                f"MDF\nUS$ {r['usd_mdf']:,.0f}",
                f"Ventas\nUS$ {r['ventas_finales']:,.0f}",
                f"Utilidad\nUS$ {r['utilidad_bruta']:,.0f}",
            ],
            color=[
                "#3b82f6", "#6366f1", "#06b6d4", "#8b5cf6", "#a855f7",
                "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#3b82f6",
                "#10b981", "#10b981",
            ],
        ),
        link=dict(
            source=[0, 0, 1, 3, 4, 4, 2, 5, 7, 9, 10],
            target=[1, 2, 3, 4, 5, 6, 7, 7, 8, 10, 11],
            value=[
                r["soles_usados"], r["soles_libres"],
                r["soles_usados"], r["usd_comprados"] * r["tc_venta"],
                r["monto_devuelto"], r["pendiente_devolver"],
                r["soles_libres"], r["monto_devuelto"],
                r["fondo_disponible"],
                r["usd_mdf"], r["utilidad_bruta"],
            ],
            color=[
                "rgba(59,130,246,0.2)", "rgba(6,182,212,0.2)",
                "rgba(99,102,241,0.2)", "rgba(139,92,246,0.2)",
                "rgba(16,185,129,0.2)", "rgba(245,158,11,0.2)",
                "rgba(6,182,212,0.2)", "rgba(16,185,129,0.2)",
                "rgba(139,92,246,0.2)",
                "rgba(59,130,246,0.2)", "rgba(16,185,129,0.2)",
            ],
        ),
    ))
    fig.update_layout(**CHART_LAYOUT, height=420, margin=dict(t=20, b=20, l=20, r=20), font=dict(size=11))
    return fig


def chart_waterfall_ventas(r):
    """Waterfall: Costo -> Utilidad -> Ventas."""
    fig = go.Figure(data=[go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=["Costo MDF", "Utilidad", "Ventas finales"],
        y=[r["usd_mdf"], r["utilidad_bruta"], r["ventas_finales"]],
        text=[f"US$ {r['usd_mdf']:,.0f}", f"US$ {r['utilidad_bruta']:,.0f}", f"US$ {r['ventas_finales']:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "rgba(128,128,128,0.3)"}},
        increasing={"marker": {"color": "#10b981"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#3b82f6"}},
    )])
    fig.update_layout(
        **CHART_LAYOUT, title="Costo vs Utilidad vs Ventas",
        height=340, margin=dict(t=50, b=30, l=40, r=40),
        font=dict(size=13), showlegend=False,
    )
    return fig


def chart_dona_capital(data, capital_total):
    """Dona: composicion del capital."""
    labels = [o["nombre"] for o in data["origen_capital"]]
    values = [o["monto"] for o in data["origen_capital"]]
    colors = ["#10b981" if "personal" in o["tipo"].lower() else "#ef4444" for o in data["origen_capital"]]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors),
        textinfo='label+percent', textposition='outside',
        pull=[0.03] * len(labels),
    )])
    fig.update_layout(
        **CHART_LAYOUT, height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False,
        annotations=[dict(text=f"S/ {capital_total:,.0f}", x=0.5, y=0.5,
                          font_size=18, font_weight=700, showarrow=False)],
    )
    return fig


def chart_op_soles(r):
    """Barras: desglose de movimiento de soles."""
    fig = go.Figure()
    vals = [r["capital_total"], r["soles_usados"], r["soles_libres"], r["soles_al_vender"], r["ganancia_tc"]]
    fig.add_trace(go.Bar(
        x=["Capital total", "Soles a USD", "Soles libres", "Soles al vender", "Ganancia"],
        y=vals,
        marker_color=["#3b82f6", "#6366f1", "#06b6d4", "#8b5cf6", "#10b981"],
        text=[f"S/ {v:,.0f}" for v in vals],
        textposition="outside", textfont=dict(size=11),
    ))
    fig.update_layout(
        **CHART_LAYOUT, title="Movimiento de soles", height=320,
        margin=dict(t=40, b=40, l=40, r=20),
        showlegend=False, yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    return fig


def chart_gauge_rentabilidad(r):
    """Gauge: rentabilidad por tipo de cambio."""
    margen = (r["ganancia_tc"] / r["soles_usados"] * 100) if r["soles_usados"] else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=margen,
        number={"suffix": "%", "font": {"size": 40}},
        title={"text": "Rentabilidad por tipo de cambio", "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, 5], "ticksuffix": "%"},
            "bar": {"color": "#10b981"},
            "bgcolor": "rgba(128,128,128,0.1)",
            "steps": [
                {"range": [0, 1], "color": "rgba(239,68,68,0.15)"},
                {"range": [1, 2], "color": "rgba(245,158,11,0.15)"},
                {"range": [2, 5], "color": "rgba(16,185,129,0.15)"},
            ],
        }
    ))
    fig.update_layout(**CHART_LAYOUT, height=320, margin=dict(t=50, b=20, l=40, r=40))
    return fig


def chart_dona_devolucion(r):
    """Dona: devuelto vs pendiente."""
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=["Devuelto", "Pendiente"],
        values=[r["monto_devuelto"], r["pendiente_devolver"]],
        hole=0.6, marker=dict(colors=["#10b981", "#f59e0b"]),
        textinfo="label+percent", textposition="outside", pull=[0.05, 0],
    ))
    fig.update_layout(
        **CHART_LAYOUT, title="Estado de devolucion", height=280,
        margin=dict(t=40, b=20, l=20, r=20), showlegend=False,
        annotations=[dict(text=f"S/ {r['soles_al_vender']:,.0f}", x=0.5, y=0.5,
                          font_size=15, font_weight=700, showarrow=False)],
    )
    return fig


def chart_mdf_waterfall(r):
    """Waterfall: desglose de fondos para MDF."""
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Costo MDF", "USD 2da compra", "USD faltantes", "Ventas"],
        y=[r["usd_mdf"], -r["usd_2da_exacto"], -r["usd_faltantes_exacto"], r["ventas_finales"]],
        text=[f"US$ {r['usd_mdf']:,.0f}", f"US$ {r['usd_2da_exacto']:,.0f}",
              f"US$ {r['usd_faltantes_exacto']:,.0f}", f"US$ {r['ventas_finales']:,.0f}"],
        textposition="outside", textfont=dict(size=11),
        connector={"line": {"color": "rgba(128,128,128,0.3)"}},
        increasing={"marker": {"color": "#10b981"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#3b82f6"}},
    ))
    fig.update_layout(
        **CHART_LAYOUT, title="Desglose de fondos para MDF", height=350,
        margin=dict(t=50, b=40, l=40, r=20),
        showlegend=False, yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    return fig


def chart_gauge_margen_melaminas(r):
    """Gauge: margen de ganancia de melaminas."""
    margen = (r["utilidad_bruta"] / r["usd_mdf"] * 100) if r["usd_mdf"] else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=margen,
        number={"suffix": "%", "font": {"size": 44}},
        delta={"reference": 20, "suffix": "%"},
        title={"text": "Margen de ganancia melaminas", "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, 50], "ticksuffix": "%"},
            "bar": {"color": "#10b981"},
            "bgcolor": "rgba(128,128,128,0.1)",
            "threshold": {"line": {"color": "#f59e0b", "width": 3}, "thickness": 0.8, "value": 20},
            "steps": [
                {"range": [0, 10], "color": "rgba(239,68,68,0.15)"},
                {"range": [10, 20], "color": "rgba(245,158,11,0.15)"},
                {"range": [20, 50], "color": "rgba(16,185,129,0.15)"},
            ],
        }
    ))
    fig.update_layout(**CHART_LAYOUT, height=350, margin=dict(t=50, b=20, l=40, r=40))
    return fig


def chart_costo_vs_venta(r):
    """Barras agrupadas: costo vs ventas vs utilidad."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Operacion MDF"], y=[r["usd_mdf"]], name="Costo MDF",
                          marker_color="#ef4444", text=f"US$ {r['usd_mdf']:,.0f}", textposition="outside"))
    fig.add_trace(go.Bar(x=["Operacion MDF"], y=[r["ventas_finales"]], name="Ventas melaminas",
                          marker_color="#10b981", text=f"US$ {r['ventas_finales']:,.0f}", textposition="outside"))
    fig.add_trace(go.Bar(x=["Operacion MDF"], y=[r["utilidad_bruta"]], name="Utilidad",
                          marker_color="#3b82f6", text=f"US$ {r['utilidad_bruta']:,.0f}", textposition="outside"))
    fig.update_layout(
        **CHART_LAYOUT, title="Costo vs Ventas vs Utilidad",
        barmode="group", height=300,
        margin=dict(t=50, b=30, l=40, r=20),
        legend=dict(orientation="h", y=-0.15),
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    return fig


def chart_simulador_barras(comparaciones, vals_real, vals_sim):
    """Barras agrupadas: Real vs Simulado."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[c[0] for c in comparaciones], y=vals_real, name="Real",
        marker_color="#6366f1",
        text=[f"{comparaciones[i][3]} {v:,.0f}" for i, v in enumerate(vals_real)],
        textposition="outside", textfont=dict(size=11),
    ))
    fig.add_trace(go.Bar(
        x=[c[0] for c in comparaciones], y=vals_sim, name="Simulado",
        marker_color="#10b981",
        text=[f"{comparaciones[i][3]} {v:,.0f}" for i, v in enumerate(vals_sim)],
        textposition="outside", textfont=dict(size=11),
    ))
    fig.update_layout(
        **CHART_LAYOUT, barmode="group", height=380,
        margin=dict(t=20, b=40, l=40, r=20),
        legend=dict(orientation="h", y=-0.12, font=dict(size=13)),
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    return fig


def chart_radar(vals_real, vals_sim):
    """Radar chart: perfil del escenario."""
    categorias = ["Capital", "Ganancia TC", "USD comprados", "Ventas", "Utilidad"]
    max_vals = [max(abs(rv), abs(sv), 1) for rv, sv in zip(vals_real, vals_sim)]
    norm_real = [rv / mv * 100 for rv, mv in zip(vals_real, max_vals)]
    norm_sim = [sv / mv * 100 for sv, mv in zip(vals_sim, max_vals)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=norm_real + [norm_real[0]], theta=categorias + [categorias[0]],
        fill="toself", name="Real",
        fillcolor="rgba(99,102,241,0.15)", line=dict(color="#6366f1", width=2),
    ))
    fig.add_trace(go.Scatterpolar(
        r=norm_sim + [norm_sim[0]], theta=categorias + [categorias[0]],
        fill="toself", name="Simulado",
        fillcolor="rgba(16,185,129,0.15)", line=dict(color="#10b981", width=2),
    ))
    fig.update_layout(
        **CHART_LAYOUT, height=380,
        margin=dict(t=30, b=30, l=60, r=60),
        legend=dict(orientation="h", y=-0.05, font=dict(size=13)),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="rgba(128,128,128,0.15)", ticksuffix="%"),
            angularaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        ),
    )
    return fig
