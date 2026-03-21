def calcular_todo(data):
    """Calcula todos los valores derivados a partir de los inputs."""
    r = {}

    # 1. Capital total
    r["capital_total"] = sum(o["monto"] for o in data["origen_capital"])
    r["total_cuotas_mes"] = sum(o["cuota"] for o in data["origen_capital"] if o["cuota"] > 0)

    # 2. Primera operacion de cambio
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

    # 3. Devolucion y fondo disponible
    r["monto_devuelto"] = data["devolucion"]["monto_devuelto"]
    r["pendiente_devolver"] = r["soles_al_vender"] - r["monto_devuelto"]
    r["fondo_disponible"] = r["soles_libres"] + r["monto_devuelto"]

    # 4. Segunda compra
    tc2 = data["segunda_compra"]["tc"]
    r["usd_2da_exacto"] = r["fondo_disponible"] / tc2 if tc2 else 0
    r["usd_2da_manual"] = data["segunda_compra"]["usd_manual"]
    r["diferencia_2da"] = r["usd_2da_manual"] - r["usd_2da_exacto"]

    # 5. MDF
    r["usd_mdf"] = data["mdf"]["usd_total"]
    r["usd_faltantes_manual"] = r["usd_mdf"] - r["usd_2da_manual"]
    r["usd_faltantes_exacto"] = r["usd_mdf"] - r["usd_2da_exacto"]
    r["soles_faltantes_manual"] = data["mdf"]["soles_faltantes_manual"]
    r["soles_faltantes_exacto"] = r["usd_faltantes_exacto"] * tc2

    # 6. Totales manuales
    r["total_liberado_manual"] = r["soles_libres"] + r["monto_devuelto"] + r["soles_faltantes_manual"]
    r["pendiente_manual"] = r["soles_al_vender"] - r["total_liberado_manual"]

    # 7. Venta final
    r["melaminas"] = data["venta_final"]["melaminas"]
    r["precio_melamina"] = data["venta_final"]["precio_por_unidad"]
    r["ventas_finales"] = r["melaminas"] * r["precio_melamina"]
    r["utilidad_bruta"] = r["ventas_finales"] - r["usd_mdf"]

    return r
