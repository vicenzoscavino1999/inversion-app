import streamlit as st
import json
import os
import plotly.graph_objects as go
from datetime import datetime
from copy import deepcopy

# ─── Configuración de página ───
st.set_page_config(
    page_title="Control de Inversiones",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "D:/inversion_app/inversiones_data.json"

# ─── Estructura de datos por defecto (basada en el Excel original) ───
DEFAULT_DATA = {
    "meta": {
        "creado": "2025-01-01",
        "ultima_modificacion": "",
        "version": 1
    },
    "origen_capital": [
        {"nombre": "Luigi", "tipo": "Capital personal", "monto": 15250, "cuota": 0, "plazo": 0, "comentario": ""},
        {"nombre": "Isabel", "tipo": "Capital personal", "monto": 20450, "cuota": 0, "plazo": 0, "comentario": ""},
        {"nombre": "Interbank", "tipo": "Prestamo", "monto": 11800, "cuota": 620, "plazo": 36, "comentario": "620 por 36 meses"},
        {"nombre": "Ripley", "tipo": "Prestamo", "monto": 24800, "cuota": 1000, "plazo": 36, "comentario": "1,000 por 36 meses"},
    ],
    "operaciones_cambio": [
        {
            "nombre": "Primera compra de dolares",
            "soles_usados": 62073,
            "tc_compra": 3.42,
            "tc_venta": 3.47,
            "activa": True,
        }
    ],
    "devolucion": {
        "monto_devuelto": 18000,
    },
    "segunda_compra": {
        "usd_manual": 8122,
        "tc": 3.47,
    },
    "mdf": {
        "usd_total": 10143,
        "soles_faltantes_manual": 7047,
    },
    "venta_final": {
        "melaminas": 2070,
        "precio_por_unidad": 5.80,
    },
    "historial": []
}


def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return deepcopy(DEFAULT_DATA)


def guardar_datos(data):
    data["meta"]["ultima_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calcular_todo(data):
    r = {}
    r["capital_total"] = sum(o["monto"] for o in data["origen_capital"])
    r["total_cuotas_mes"] = sum(o["cuota"] for o in data["origen_capital"] if o["cuota"] > 0)

    op = data["operaciones_cambio"][0] if data["operaciones_cambio"] else None
    if op:
        r["soles_usados"] = op["soles_usados"]
        r["soles_libres"] = r["capital_total"] - op["soles_usados"]
        r["tc_compra"] = op["tc_compra"]
        r["tc_venta"] = op["tc_venta"]
        r["usd_comprados"] = op["soles_usados"] / op["tc_compra"] if op["tc_compra"] else 0
        r["soles_al_vender"] = r["usd_comprados"] * op["tc_venta"]
        r["ganancia_tc"] = r["soles_al_vender"] - op["soles_usados"]
    else:
        r["soles_usados"] = 0
        r["soles_libres"] = r["capital_total"]
        r["tc_compra"] = 0
        r["tc_venta"] = 0
        r["usd_comprados"] = 0
        r["soles_al_vender"] = 0
        r["ganancia_tc"] = 0

    r["monto_devuelto"] = data["devolucion"]["monto_devuelto"]
    r["pendiente_devolver"] = r["soles_al_vender"] - r["monto_devuelto"]
    r["fondo_disponible"] = r["soles_libres"] + r["monto_devuelto"]

    tc2 = data["segunda_compra"]["tc"]
    r["usd_2da_exacto"] = r["fondo_disponible"] / tc2 if tc2 else 0
    r["usd_2da_manual"] = data["segunda_compra"]["usd_manual"]
    r["diferencia_2da"] = r["usd_2da_manual"] - r["usd_2da_exacto"]

    r["usd_mdf"] = data["mdf"]["usd_total"]
    r["usd_faltantes_manual"] = r["usd_mdf"] - r["usd_2da_manual"]
    r["usd_faltantes_exacto"] = r["usd_mdf"] - r["usd_2da_exacto"]
    r["soles_faltantes_manual"] = data["mdf"]["soles_faltantes_manual"]
    r["soles_faltantes_exacto"] = r["usd_faltantes_exacto"] * tc2

    r["total_liberado_manual"] = r["soles_libres"] + r["monto_devuelto"] + r["soles_faltantes_manual"]
    r["pendiente_manual"] = r["soles_al_vender"] - r["total_liberado_manual"]

    r["melaminas"] = data["venta_final"]["melaminas"]
    r["precio_melamina"] = data["venta_final"]["precio_por_unidad"]
    r["ventas_finales"] = r["melaminas"] * r["precio_melamina"]
    r["utilidad_bruta"] = r["ventas_finales"] - r["usd_mdf"]

    return r


# ─── Helpers de UI ───
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
    """Header de sección con número de paso."""
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


def barra_progreso_html(valor, maximo, color="#4CAF50", label=""):
    """Barra de progreso visual."""
    pct = min((valor / maximo * 100) if maximo else 0, 100)
    return f"""
    <div style="margin: 8px 0;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span>{label}</span>
            <span style="font-weight: 600;">{pct:.1f}%</span>
        </div>
        <div style="background: rgba(128,128,128,0.2); border-radius: 8px; height: 10px; overflow: hidden;">
            <div style="
                background: linear-gradient(90deg, {color}, {color}cc);
                width: {pct}%; height: 100%; border-radius: 8px;
                transition: width 0.5s ease;
            "></div>
        </div>
    </div>
    """


def flecha_flujo():
    """Flecha visual entre pasos."""
    st.markdown("""
    <div style="text-align: center; margin: 8px 0; opacity: 0.4; font-size: 1.4rem;">
        ⬇
    </div>
    """, unsafe_allow_html=True)


# ─── Cargar datos ───
if "data" not in st.session_state:
    st.session_state.data = cargar_datos()

data = st.session_state.data
r = calcular_todo(data)

# ─── CSS Global ───
st.markdown("""
<style>
    .block-container { padding-top: 1rem; max-width: 1200px; }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border-radius: 10px;
        padding: 14px 18px;
        border: 1px solid rgba(128,128,128,0.15);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--secondary-background-color);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-weight: 500;
    }

    /* Botones primarios */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* Info/Success/Warning boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div style="
    text-align: center;
    padding: 16px 0 8px 0;
">
    <div style="font-size: 2.2rem; font-weight: 800; letter-spacing: -1px;">
        📈 Control de Inversiones
    </div>
    <div style="font-size: 0.95rem; opacity: 0.6; margin-top: 4px;">
        Gestiona y simula tus inversiones paso a paso
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# RESUMEN RÁPIDO (tarjetas superiores)
# ═══════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ═══════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "  Resumen  ",
    "  Capital  ",
    "  Cambio  ",
    "  MDF y Venta  ",
    "  Simulador  ",
    "  Historial  ",
])


# ───────────────────────────────────────────────────────────
# TAB 1: RESUMEN GENERAL
# ───────────────────────────────────────────────────────────
with tab1:

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

    # Grafico barras horizontales: composicion del capital
    fig_cap_bar = go.Figure()
    for o in data["origen_capital"]:
        es_p = "prestamo" in o["tipo"].lower()
        fig_cap_bar.add_trace(go.Bar(
            y=["Capital"], x=[o["monto"]], name=o["nombre"],
            orientation="h",
            marker_color="#ef4444" if es_p else "#10b981",
            text=f"{o['nombre']}: S/ {o['monto']:,.0f}",
            textposition="inside", textfont=dict(color="white", size=12),
            hovertemplate=f"<b>{o['nombre']}</b><br>S/ {o['monto']:,.0f}<br>{o['tipo']}<extra></extra>",
        ))
    fig_cap_bar.update_layout(
        barmode="stack", template="plotly_dark", height=80,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    st.plotly_chart(fig_cap_bar, use_container_width=True)

    flecha_flujo()

    # ── Paso 2: Compra de USD ──
    seccion("Primera compra de dolares", "2", f"S/ {r['soles_usados']:,.0f} entran a dolares, S/ {r['soles_libres']:,.0f} quedan libres")

    p2a, p2b, p2c, p2d = st.columns(4)
    with p2a:
        st.markdown(tarjeta("SOLES INVERTIDOS", f"S/ {r['soles_usados']:,.0f}", "#3b82f6", "💵"), unsafe_allow_html=True)
    with p2b:
        st.markdown(tarjeta("USD COMPRADOS", f"US$ {r['usd_comprados']:,.0f}", "#06b6d4", "💲"), unsafe_allow_html=True)
    with p2c:
        st.markdown(tarjeta("SOLES AL VENDER", f"S/ {r['soles_al_vender']:,.2f}", "#8b5cf6", "💸"), unsafe_allow_html=True)
    with p2d:
        st.markdown(tarjeta("GANANCIA", f"S/ {r['ganancia_tc']:,.2f}", "#10b981", "✅"), unsafe_allow_html=True)

    # Grafico: Barras comparativas Soles invertidos vs Soles al vender
    fig_cambio = go.Figure()
    fig_cambio.add_trace(go.Bar(
        x=["Soles invertidos", "Soles al vender", "Ganancia"],
        y=[r["soles_usados"], r["soles_al_vender"], r["ganancia_tc"]],
        marker_color=["#3b82f6", "#8b5cf6", "#10b981"],
        text=[f"S/ {r['soles_usados']:,.0f}", f"S/ {r['soles_al_vender']:,.2f}", f"S/ {r['ganancia_tc']:,.2f}"],
        textposition="outside", textfont=dict(size=13),
        hovertemplate="%{x}<br><b>%{text}</b><extra></extra>",
    ))
    fig_cambio.update_layout(
        template="plotly_dark", height=300,
        margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    st.plotly_chart(fig_cambio, use_container_width=True)

    # Flujo visual compra/venta
    st.markdown(f"""
    <div style="
        background: var(--secondary-background-color);
        border-radius: 12px; padding: 16px 24px; margin: 4px 0;
        display: flex; align-items: center; justify-content: center; gap: 16px;
        flex-wrap: wrap; font-size: 0.9rem;
    ">
        <span style="font-weight: 600;">S/ {r['soles_usados']:,.0f}</span>
        <span style="opacity: 0.5;">→ compra a</span>
        <span style="
            background: #3b82f6; color: white; padding: 4px 12px;
            border-radius: 20px; font-weight: 600;
        ">{r['tc_compra']:.2f}</span>
        <span style="opacity: 0.5;">→</span>
        <span style="font-weight: 600;">US$ {r['usd_comprados']:,.0f}</span>
        <span style="opacity: 0.5;">→ venta a</span>
        <span style="
            background: #10b981; color: white; padding: 4px 12px;
            border-radius: 20px; font-weight: 600;
        ">{r['tc_venta']:.2f}</span>
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

    # Grafico gauge: % devuelto
    pct_devuelto = (r["monto_devuelto"] / r["soles_al_vender"] * 100) if r["soles_al_vender"] else 0
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct_devuelto,
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
    fig_gauge.update_layout(
        template="plotly_dark", height=250,
        margin=dict(t=40, b=20, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Grafico: composicion del fondo disponible
    fig_fondo = go.Figure()
    fig_fondo.add_trace(go.Bar(
        y=["Fondo disponible"], x=[r["soles_libres"]], name="Soles libres",
        orientation="h", marker_color="#3b82f6",
        text=f"Libres: S/ {r['soles_libres']:,.0f}", textposition="inside",
        textfont=dict(color="white", size=12),
    ))
    fig_fondo.add_trace(go.Bar(
        y=["Fondo disponible"], x=[r["monto_devuelto"]], name="Devuelto",
        orientation="h", marker_color="#10b981",
        text=f"Devuelto: S/ {r['monto_devuelto']:,.0f}", textposition="inside",
        textfont=dict(color="white", size=12),
    ))
    fig_fondo.update_layout(
        barmode="stack", template="plotly_dark", height=70,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True, legend=dict(orientation="h", y=-0.3),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    st.plotly_chart(fig_fondo, use_container_width=True)

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

    # ── Diagrama Sankey: flujo completo del dinero ──
    seccion("Flujo completo del dinero", "📊", "Como se mueve el capital desde el origen hasta la venta final")

    # Nodos: 0=Capital, 1=Soles a USD, 2=Soles libres, 3=USD 1ra, 4=Soles venta,
    #         5=Devuelto, 6=Pendiente, 7=Fondo disp, 8=USD 2da, 9=MDF, 10=Melaminas, 11=Utilidad
    fig_sankey = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20, thickness=25,
            label=[
                f"Capital Total\nS/ {r['capital_total']:,.0f}",      # 0
                f"Compra USD\nS/ {r['soles_usados']:,.0f}",          # 1
                f"Soles libres\nS/ {r['soles_libres']:,.0f}",        # 2
                f"USD 1ra\nUS$ {r['usd_comprados']:,.0f}",           # 3
                f"Venta USD\nS/ {r['soles_al_vender']:,.0f}",        # 4
                f"Devuelto\nS/ {r['monto_devuelto']:,.0f}",          # 5
                f"Pendiente\nS/ {r['pendiente_devolver']:,.0f}",     # 6
                f"Fondo disp.\nS/ {r['fondo_disponible']:,.0f}",     # 7
                f"USD 2da\nUS$ {r['usd_2da_exacto']:,.0f}",         # 8
                f"MDF\nUS$ {r['usd_mdf']:,.0f}",                     # 9
                f"Ventas\nUS$ {r['ventas_finales']:,.0f}",           # 10
                f"Utilidad\nUS$ {r['utilidad_bruta']:,.0f}",         # 11
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
    fig_sankey.update_layout(
        template="plotly_dark", height=420,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    # ── Waterfall: Costo → Utilidad → Ventas ──
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
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
        title="Costo vs Utilidad vs Ventas",
        template="plotly_dark",
        height=340,
        margin=dict(t=50, b=30, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ───────────────────────────────────────────────────────────
# TAB 2: ORIGEN DEL CAPITAL (editable)
# ───────────────────────────────────────────────────────────
with tab2:
    seccion("Origen del Capital", "💵", "Edita los montos o agrega nuevas fuentes")

    # Grafico de dona
    labels = [o["nombre"] for o in data["origen_capital"]]
    values = [o["monto"] for o in data["origen_capital"]]
    colors = ["#10b981" if "personal" in o["tipo"].lower() else "#ef4444" for o in data["origen_capital"]]

    fig_cap = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='outside',
        pull=[0.03] * len(labels),
    )])
    fig_cap.update_layout(
        template="plotly_dark",
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[dict(text=f"S/ {r['capital_total']:,.0f}", x=0.5, y=0.5,
                          font_size=18, font_weight=700, showarrow=False)],
    )
    st.plotly_chart(fig_cap, use_container_width=True)

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


# ───────────────────────────────────────────────────────────
# TAB 3: OPERACIÓN CAMBIARIA
# ───────────────────────────────────────────────────────────
with tab3:
    seccion("Operacion Cambiaria", "🔄", "Compra y venta de dolares")

    cambios_op = False

    # ── Primera operacion ──
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

    # ── Devolucion ──
    st.markdown("##### Devolucion")
    new_devuelto = st.number_input("Monto devuelto (S/)", value=float(data["devolucion"]["monto_devuelto"]),
                                    step=500.0, key="devuelto")
    if new_devuelto != data["devolucion"]["monto_devuelto"]:
        data["devolucion"]["monto_devuelto"] = new_devuelto
        cambios_op = True

    # ── Segunda compra ──
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

    # Grafico: flujo de la operacion cambiaria
    st.markdown("---")
    st.markdown("##### Visualizacion de la operacion")

    fig_op_col1, fig_op_col2 = st.columns(2)

    with fig_op_col1:
        # Barras: desglose de soles
        fig_soles = go.Figure()
        fig_soles.add_trace(go.Bar(
            x=["Capital total", "Soles a USD", "Soles libres", "Soles al vender", "Ganancia"],
            y=[r_temp["capital_total"], r_temp["soles_usados"], r_temp["soles_libres"],
               r_temp["soles_al_vender"], r_temp["ganancia_tc"]],
            marker_color=["#3b82f6", "#6366f1", "#06b6d4", "#8b5cf6", "#10b981"],
            text=[f"S/ {v:,.0f}" for v in [r_temp["capital_total"], r_temp["soles_usados"],
                  r_temp["soles_libres"], r_temp["soles_al_vender"], r_temp["ganancia_tc"]]],
            textposition="outside", textfont=dict(size=11),
        ))
        fig_soles.update_layout(
            title="Movimiento de soles", template="plotly_dark", height=320,
            margin=dict(t=40, b=40, l=40, r=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False, yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
        )
        st.plotly_chart(fig_soles, use_container_width=True)

    with fig_op_col2:
        # Gauge: margen de ganancia TC
        margen_tc = (r_temp["ganancia_tc"] / r_temp["soles_usados"] * 100) if r_temp["soles_usados"] else 0
        fig_margen = go.Figure(go.Indicator(
            mode="gauge+number",
            value=margen_tc,
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
        fig_margen.update_layout(
            template="plotly_dark", height=320,
            margin=dict(t=50, b=20, l=40, r=40),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_margen, use_container_width=True)

    # Grafico: devolucion vs pendiente
    fig_dev = go.Figure()
    fig_dev.add_trace(go.Pie(
        labels=["Devuelto", "Pendiente"],
        values=[r_temp["monto_devuelto"], r_temp["pendiente_devolver"]],
        hole=0.6,
        marker=dict(colors=["#10b981", "#f59e0b"]),
        textinfo="label+percent",
        textposition="outside",
        pull=[0.05, 0],
    ))
    fig_dev.update_layout(
        title="Estado de devolucion", template="plotly_dark", height=280,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[dict(text=f"S/ {r_temp['soles_al_vender']:,.0f}", x=0.5, y=0.5,
                          font_size=15, font_weight=700, showarrow=False)],
    )
    st.plotly_chart(fig_dev, use_container_width=True)

    if cambios_op:
        if st.button("Guardar cambios en operacion", type="primary", key="save_op"):
            guardar_datos(data)
            st.success("Cambios guardados.")
            st.rerun()


# ───────────────────────────────────────────────────────────
# TAB 4: MDF Y VENTA
# ───────────────────────────────────────────────────────────
with tab4:
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

    r_temp2 = calcular_todo(data)

    st.markdown("---")
    st.markdown("##### Resultados calculados")

    rm1, rm2, rm3 = st.columns(3)
    with rm1:
        st.markdown(tarjeta("USD FALTANTES", f"US$ {r_temp2['usd_faltantes_exacto']:,.2f}", "#ef4444", "⚠"), unsafe_allow_html=True)
    with rm2:
        st.markdown(tarjeta("VENTAS PROYECTADAS", f"US$ {r_temp2['ventas_finales']:,.0f}", "#3b82f6", "📈"), unsafe_allow_html=True)
    with rm3:
        color_u2 = "#10b981" if r_temp2['utilidad_bruta'] >= 0 else "#ef4444"
        margen = (r_temp2['utilidad_bruta']/r_temp2['usd_mdf']*100) if r_temp2['usd_mdf'] else 0
        st.markdown(tarjeta("UTILIDAD BRUTA", f"US$ {r_temp2['utilidad_bruta']:,.0f}", color_u2, "🎯",
                            f"Margen: {margen:.1f}%"), unsafe_allow_html=True)

    rm4, rm5 = st.columns(2)
    with rm4:
        st.markdown(tarjeta("PENDIENTE (MANUAL)", f"S/ {r_temp2['pendiente_manual']:,.2f}", "#f59e0b", "⏳"), unsafe_allow_html=True)
    with rm5:
        st.markdown(tarjeta("LIBERADO/DEVUELTO", f"S/ {r_temp2['total_liberado_manual']:,.0f}", "#10b981", "✅"), unsafe_allow_html=True)

    # Graficos MDF y Venta
    st.markdown("---")
    st.markdown("##### Visualizacion de costos y ganancias")

    fig_mdf_col1, fig_mdf_col2 = st.columns(2)

    with fig_mdf_col1:
        # Waterfall: desglose de la operacion MDF
        fig_mdf_w = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Costo MDF", "USD 2da compra", "USD faltantes", "Ventas"],
            y=[r_temp2["usd_mdf"], -r_temp2["usd_2da_exacto"], -r_temp2["usd_faltantes_exacto"], r_temp2["ventas_finales"]],
            text=[f"US$ {r_temp2['usd_mdf']:,.0f}", f"US$ {r_temp2['usd_2da_exacto']:,.0f}",
                  f"US$ {r_temp2['usd_faltantes_exacto']:,.0f}", f"US$ {r_temp2['ventas_finales']:,.0f}"],
            textposition="outside", textfont=dict(size=11),
            connector={"line": {"color": "rgba(128,128,128,0.3)"}},
            increasing={"marker": {"color": "#10b981"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}},
        ))
        fig_mdf_w.update_layout(
            title="Desglose de fondos para MDF", template="plotly_dark", height=350,
            margin=dict(t=50, b=40, l=40, r=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False, yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
        )
        st.plotly_chart(fig_mdf_w, use_container_width=True)

    with fig_mdf_col2:
        # Gauge: margen de la venta de melaminas
        margen_mel = (r_temp2["utilidad_bruta"] / r_temp2["usd_mdf"] * 100) if r_temp2["usd_mdf"] else 0
        fig_margen_mel = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=margen_mel,
            number={"suffix": "%", "font": {"size": 44}},
            delta={"reference": 20, "suffix": "%"},
            title={"text": "Margen de ganancia melaminas", "font": {"size": 13}},
            gauge={
                "axis": {"range": [0, 50], "ticksuffix": "%"},
                "bar": {"color": "#10b981"},
                "bgcolor": "rgba(128,128,128,0.1)",
                "threshold": {
                    "line": {"color": "#f59e0b", "width": 3},
                    "thickness": 0.8, "value": 20,
                },
                "steps": [
                    {"range": [0, 10], "color": "rgba(239,68,68,0.15)"},
                    {"range": [10, 20], "color": "rgba(245,158,11,0.15)"},
                    {"range": [20, 50], "color": "rgba(16,185,129,0.15)"},
                ],
            }
        ))
        fig_margen_mel.update_layout(
            template="plotly_dark", height=350,
            margin=dict(t=50, b=20, l=40, r=40),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_margen_mel, use_container_width=True)

    # Grafico: Costo vs Venta (barras lado a lado)
    fig_cv = go.Figure()
    fig_cv.add_trace(go.Bar(
        x=["Operacion MDF"], y=[r_temp2["usd_mdf"]], name="Costo MDF",
        marker_color="#ef4444", text=f"US$ {r_temp2['usd_mdf']:,.0f}",
        textposition="outside",
    ))
    fig_cv.add_trace(go.Bar(
        x=["Operacion MDF"], y=[r_temp2["ventas_finales"]], name="Ventas melaminas",
        marker_color="#10b981", text=f"US$ {r_temp2['ventas_finales']:,.0f}",
        textposition="outside",
    ))
    fig_cv.add_trace(go.Bar(
        x=["Operacion MDF"], y=[r_temp2["utilidad_bruta"]], name="Utilidad",
        marker_color="#3b82f6", text=f"US$ {r_temp2['utilidad_bruta']:,.0f}",
        textposition="outside",
    ))
    fig_cv.update_layout(
        title="Costo vs Ventas vs Utilidad",
        barmode="group", template="plotly_dark", height=300,
        margin=dict(t=50, b=30, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.15),
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    st.plotly_chart(fig_cv, use_container_width=True)

    if cambios_mdf:
        if st.button("Guardar cambios en MDF/Venta", type="primary", key="save_mdf"):
            guardar_datos(data)
            st.success("Cambios guardados.")
            st.rerun()


# ───────────────────────────────────────────────────────────
# TAB 5: SIMULADOR
# ───────────────────────────────────────────────────────────
with tab5:
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

    # Grafico comparativo: barras agrupadas Real vs Simulado
    st.markdown("---")
    st.markdown("##### Grafico comparativo")

    labels_sim = [c[0] for c in comparaciones]
    vals_real = [c[1] for c in comparaciones]
    vals_sim = [c[2] for c in comparaciones]

    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(
        x=labels_sim, y=vals_real, name="Real",
        marker_color="#6366f1",
        text=[f"{comparaciones[i][3]} {v:,.0f}" for i, v in enumerate(vals_real)],
        textposition="outside", textfont=dict(size=11),
    ))
    fig_sim.add_trace(go.Bar(
        x=labels_sim, y=vals_sim, name="Simulado",
        marker_color="#10b981",
        text=[f"{comparaciones[i][3]} {v:,.0f}" for i, v in enumerate(vals_sim)],
        textposition="outside", textfont=dict(size=11),
    ))
    fig_sim.update_layout(
        barmode="group", template="plotly_dark", height=380,
        margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.12, font=dict(size=13)),
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    )
    st.plotly_chart(fig_sim, use_container_width=True)

    # Radar chart: perfil del escenario
    categorias_radar = ["Capital", "Ganancia TC", "USD comprados", "Ventas", "Utilidad"]
    # Normalizar a porcentaje del real
    max_vals = [max(abs(rv), abs(sv), 1) for rv, sv in zip(vals_real, vals_sim)]
    norm_real = [rv / mv * 100 for rv, mv in zip(vals_real, max_vals)]
    norm_sim = [sv / mv * 100 for sv, mv in zip(vals_sim, max_vals)]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=norm_real + [norm_real[0]], theta=categorias_radar + [categorias_radar[0]],
        fill="toself", name="Real",
        fillcolor="rgba(99,102,241,0.15)", line=dict(color="#6366f1", width=2),
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=norm_sim + [norm_sim[0]], theta=categorias_radar + [categorias_radar[0]],
        fill="toself", name="Simulado",
        fillcolor="rgba(16,185,129,0.15)", line=dict(color="#10b981", width=2),
    ))
    fig_radar.update_layout(
        template="plotly_dark", height=380,
        margin=dict(t=30, b=30, l=60, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.05, font=dict(size=13)),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="rgba(128,128,128,0.15)", ticksuffix="%"),
            angularaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        ),
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ───────────────────────────────────────────────────────────
# TAB 6: HISTORIAL
# ───────────────────────────────────────────────────────────
with tab6:
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


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
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
    if st.button("Resetear a datos del Excel", type="secondary"):
        st.session_state.data = deepcopy(DEFAULT_DATA)
        guardar_datos(st.session_state.data)
        st.success("Datos reseteados.")
        st.rerun()

    st.markdown("---")
    st.caption("Datos guardados en inversiones_data.json")
