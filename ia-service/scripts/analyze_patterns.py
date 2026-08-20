"""Análisis descriptivo reproducible de T39 con reserva temporal protegida."""

import csv
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, median, pstdev

BASE = Path(__file__).resolve().parent.parent
SOURCE = BASE / "data" / "simulated_expenses.csv"
OUT = BASE / "analysis"
SUMMARY = OUT / "patterns_summary.json"
REPORT = OUT / "patterns_report.md"
DAILY = OUT / "daily_spending_analysis.csv"
DEV_END = date(2025, 12, 31)
HOLDOUT_START = date(2026, 1, 1)
CATEGORIES = ["Alimentación", "Transporte", "Vivienda", "Servicios básicos", "Salud",
              "Educación", "Pago de deudas y créditos", "Entretenimiento", "Mascotas", "Otros gastos"]
CANDIDATES = ["spend_last_7_days", "spend_last_14_days", "transactions_last_7_days",
              "transactions_last_14_days", "spend_change_last_7_vs_previous_7",
              "transaction_count_change_last_7_vs_previous_7", "recent_daily_spend_rate",
              "average_transaction_amount", "median_transaction_amount", "max_transaction_amount",
              "active_spending_days", "days_since_last_expense", "category_share",
              "previous_month_comparable_spend", "previous_month_comparable_transactions",
              "category_previous_month_comparable_spend", "transaction_frequency_spend_correlation",
              "cumulative_spend_slope"]


def rnd(value, digits=2):
    value = round(float(value), digits)
    if not math.isfinite(value):
        raise ValueError("Valor numérico no finito.")
    return value


def change(current, previous):
    return {"absolute": rnd(current - previous),
            "percentage": rnd((current - previous) / previous * 100) if previous else None,
            "status": "calculada" if previous else ("sin base porcentual" if current else "sin variación")}


def load():
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["date", "category", "amount"]:
            raise ValueError("Columnas inesperadas.")
        for source in reader:
            row = {"date": date.fromisoformat(source["date"]), "category": source["category"],
                   "amount": float(source["amount"])}
            if row["category"] not in CATEGORIES or row["amount"] <= 0:
                raise ValueError("Categoría o monto inválido.")
            rows.append(row)
    return sorted(rows, key=lambda item: (item["date"], item["category"], item["amount"]))


def months(start, end):
    result, year, month = [], start.year, start.month
    while (year, month) <= (end.year, end.month):
        result.append(f"{year:04d}-{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result


def between(rows, start, end, category=None):
    return [row for row in rows if start <= row["date"] <= end
            and (category is None or row["category"] == category)]


def aggregate(rows):
    values = [row["amount"] for row in rows]
    return {"spend": rnd(sum(values)), "transactions": len(values),
            "average_transaction_amount": rnd(mean(values)) if values else 0.0,
            "median_transaction_amount": rnd(median(values)) if values else 0.0,
            "max_transaction_amount": rnd(max(values)) if values else 0.0}


def daily_series(rows, start, end):
    grouped = defaultdict(list)
    for row in between(rows, start, end):
        grouped[row["date"]].append(row["amount"])
    output, current = [], start
    while current <= end:
        values = grouped[current]
        output.append({"date": current.isoformat(), "daily_transaction_count": len(values),
                       "daily_spend": rnd(sum(values)),
                       "average_transaction_amount": rnd(mean(values)) if values else 0.0})
        current += timedelta(days=1)
    return output


def pearson(left, right):
    left_mean, right_mean = mean(left), mean(right)
    numerator = sum((x-left_mean)*(y-right_mean) for x, y in zip(left, right))
    denominator = math.sqrt(sum((x-left_mean)**2 for x in left)*sum((y-right_mean)**2 for y in right))
    return rnd(numerator/denominator, 6) if denominator else 0.0


def ranks(values):
    ordered, result, index = sorted(enumerate(values), key=lambda item: item[1]), [0.0]*len(values), 0
    while index < len(ordered):
        end = index
        while end+1 < len(ordered) and ordered[end+1][1] == ordered[index][1]:
            end += 1
        rank = (index+end+2)/2
        for position in range(index, end+1):
            result[ordered[position][0]] = rank
        index = end+1
    return result


def slope(values):
    x_mean, y_mean = (len(values)-1)/2, mean(values)
    denominator = sum((i-x_mean)**2 for i in range(len(values)))
    return rnd(sum((i-x_mean)*(value-y_mean) for i, value in enumerate(values))/denominator) if denominator else 0.0


def windows(rows, cutoff, category=None):
    last7 = aggregate(between(rows, cutoff-timedelta(days=6), cutoff, category))
    prev7 = aggregate(between(rows, cutoff-timedelta(days=13), cutoff-timedelta(days=7), category))
    last14 = aggregate(between(rows, cutoff-timedelta(days=13), cutoff, category))
    for item, days in [(last7, 7), (prev7, 7), (last14, 14)]:
        item["daily_spend_rate"] = rnd(item["spend"]/days)
    return {"cutoff_date": cutoff.isoformat(), "previous_7_days": prev7, "last_7_days": last7,
            "last_14_days": last14, "changes_last_7_vs_previous_7": {
                "spend": change(last7["spend"], prev7["spend"]),
                "transactions": change(last7["transactions"], prev7["transactions"]),
                "average_transaction_amount": change(last7["average_transaction_amount"],
                                                     prev7["average_transaction_amount"])}}


def previous_month(rows, cutoff):
    previous_end = cutoff.replace(day=1)-timedelta(days=1)
    equivalent_day = min(cutoff.day, previous_end.day)
    current_start, previous_start = cutoff.replace(day=1), previous_end.replace(day=1)
    current_end, previous_equal_end = cutoff.replace(day=equivalent_day), previous_end.replace(day=equivalent_day)
    current = aggregate(between(rows, current_start, current_end))
    previous = aggregate(between(rows, previous_start, previous_equal_end))
    current["average_daily_spend"], previous["average_daily_spend"] = (
        rnd(current["spend"]/equivalent_day), rnd(previous["spend"]/equivalent_day))
    by_category = []
    for category in CATEGORIES:
        now = aggregate(between(rows, current_start, current_end, category))
        before = aggregate(between(rows, previous_start, previous_equal_end, category))
        by_category.append({"category": category, "previous_spend": before["spend"],
                            "current_spend": now["spend"], "spend_change": change(now["spend"], before["spend"])})
    return {"previous_equivalent_period": f"{previous_start} a {previous_equal_end}",
            "current_period": f"{current_start} a {current_end}",
            "equivalent_days": equivalent_day, "previous": previous, "current": current,
            "changes": {"spend": change(current["spend"], previous["spend"]),
                        "transactions": change(current["transactions"], previous["transactions"]),
                        "average_daily_spend": change(current["average_daily_spend"], previous["average_daily_spend"]),
                        "average_transaction_amount": change(current["average_transaction_amount"],
                                                             previous["average_transaction_amount"])},
            "category_changes": by_category}


def trend(rows, cutoff):
    start, days = cutoff.replace(day=1), cutoff.day
    first_days = max(1, days//2)
    first_end, second_start = start+timedelta(days=first_days-1), start+timedelta(days=first_days)
    first, second = aggregate(between(rows, start, first_end)), aggregate(between(rows, second_start, cutoff))
    second_days = max(1, days-first_days)
    first_rate, second_rate = first["spend"]/first_days, second["spend"]/second_days
    variation = change(second_rate, first_rate)
    percent = variation["percentage"]
    direction = "sin base suficiente" if percent is None else (
        "aceleración" if percent > 10 else "desaceleración" if percent < -10 else "estabilidad")
    running, cumulative = 0.0, []
    for item in daily_series(rows, start, cutoff):
        running += item["daily_spend"]
        cumulative.append(running)
    return {"thresholds": "aceleración > 10 %, desaceleración < -10 %, estabilidad entre -10 % y 10 %",
            "first_half": {**first, "days": first_days, "daily_spend_rate": rnd(first_rate)},
            "second_half": {**second, "days": second_days, "daily_spend_rate": rnd(second_rate)},
            "second_vs_first_daily_rate": variation, "direction": direction,
            "cumulative_spend_slope_per_day": slope(cumulative)}


def categories(rows, cutoff, total):
    periods = months(rows[0]["date"], cutoff)
    result = []
    for category in CATEGORIES:
        selected = [row for row in rows if row["category"] == category and row["date"] <= cutoff]
        values, monthly = [row["amount"] for row in selected], defaultdict(float)
        for row in selected:
            monthly[row["date"].strftime("%Y-%m")] += row["amount"]
        monthly_values = [monthly.get(period, 0.0) for period in periods]
        recent = windows(rows, cutoff, category)
        percent = recent["changes_last_7_vs_previous_7"]["spend"]["percentage"]
        direction = "sin base suficiente" if percent is None else (
            "aceleración" if percent > 10 else "desaceleración" if percent < -10 else "estabilidad")
        average_monthly, deviation = mean(monthly_values), pstdev(monthly_values)
        result.append({"category": category, "total_spend": rnd(sum(values)), "transactions": len(values),
                       "average_transaction_amount": rnd(mean(values)), "median_transaction_amount": rnd(median(values)),
                       "spending_share_percentage": rnd(sum(values)/total*100),
                       "transaction_frequency_per_month": rnd(len(values)/len(periods)),
                       "days_since_last_transaction": (cutoff-max(row["date"] for row in selected)).days,
                       "historical_weight_percentage": rnd(sum(values)/total*100),
                       "monthly_standard_deviation": rnd(deviation),
                       "monthly_coefficient_of_variation": rnd(deviation/average_monthly, 4) if average_monthly else None,
                       "last_7_days_spend": recent["last_7_days"]["spend"],
                       "last_7_days_transactions": recent["last_7_days"]["transactions"],
                       "last_7_vs_previous_7_spend_change": recent["changes_last_7_vs_previous_7"]["spend"],
                       "recent_direction": direction})
    return result


def decompositions(rows):
    candidates = []
    cutoff = rows[0]["date"]+timedelta(days=13)
    while cutoff <= DEV_END:
        data = windows(rows, cutoff); now, before = data["last_7_days"], data["previous_7_days"]
        if now["spend"] > before["spend"] and now["transactions"] and before["transactions"]:
            frequency = (now["transactions"]-before["transactions"])*before["average_transaction_amount"]
            amount = now["transactions"]*(now["average_transaction_amount"]-before["average_transaction_amount"])
            driver = "ambos factores" if frequency > 0 and amount > 0 else (
                "mayor frecuencia" if frequency > amount else "mayor monto promedio")
            candidates.append({"cutoff_date": cutoff.isoformat(),
                "previous_period": f"{cutoff-timedelta(days=13)} a {cutoff-timedelta(days=7)}",
                "current_period": f"{cutoff-timedelta(days=6)} a {cutoff}",
                "previous_spend": before["spend"], "current_spend": now["spend"],
                "previous_transactions": before["transactions"], "current_transactions": now["transactions"],
                "previous_average_transaction": before["average_transaction_amount"],
                "current_average_transaction": now["average_transaction_amount"],
                "frequency_contribution": rnd(frequency), "average_amount_contribution": rnd(amount),
                "main_association": driver})
        cutoff += timedelta(days=1)
    result = []
    for driver in ["mayor frecuencia", "mayor monto promedio", "ambos factores"]:
        matches = [item for item in candidates if item["main_association"] == driver]
        if matches:
            result.append(max(matches, key=lambda item: item["current_spend"]-item["previous_spend"]))
    return result


def patterns(metrics, correlation, recent, rhythm, period):
    dominant = max(metrics, key=lambda item: item["spending_share_percentage"])
    frequent = max(metrics, key=lambda item: item["transactions"])
    stable = min((item for item in metrics if item != dominant),
                 key=lambda item: item["monthly_coefficient_of_variation"] or float("inf"))
    return [
        {"id": "P01", "name": f"Participación monetaria dominante de {dominant['category']}",
         "metric": "spending_share_percentage", "value": dominant["spending_share_percentage"], "period": period,
         "interpretation": "Mayor peso monetario del período de desarrollo.", "limitation": "Escenario simulado."},
        {"id": "P02", "name": f"Frecuencia dominante de {frequent['category']}", "metric": "transactions",
         "value": frequent["transactions"], "period": period,
         "interpretation": "Mayor cantidad de transacciones.", "limitation": "Frecuencia no equivale a gasto total."},
        {"id": "P03", "name": f"Estabilidad mensual relativa de {stable['category']}",
         "metric": "monthly_coefficient_of_variation", "value": stable["monthly_coefficient_of_variation"],
         "period": period, "interpretation": "Menor dispersión relativa entre categorías no dominantes.",
         "limitation": "Puede no repetirse fuera del dataset."},
        {"id": "P04", "name": "Asociación entre frecuencia diaria y gasto diario", "metric": "pearson",
         "value": correlation["pearson"], "period": period,
         "interpretation": "Asociación estadística cuantificada.",
         "limitation": "Una correlación estadística no permite establecer causalidad."},
        {"id": "P05", "name": f"Ritmo reciente: {rhythm['direction']}",
         "metric": "spend_change_last_7_vs_previous_7",
         "value": recent["changes_last_7_vs_previous_7"]["spend"]["percentage"],
         "period": f"corte {recent['cutoff_date']}",
         "interpretation": "Cambio entre ventanas equivalentes.", "limitation": "Sensible a gastos puntuales."}]


def money(value):
    return f"${value:,.0f}".replace(",", ".")


def build_report(data):
    dev, general = data["development_analysis"], data["development_analysis"]["general_metrics"]
    recent, corr, previous = dev["recent_windows"], dev["daily_frequency_spend_correlation"], dev["previous_month_equivalent_comparison"]
    category_rows = "\n".join(f"| {x['category']} | {money(x['total_spend'])} | {x['transactions']} | "
        f"{money(x['average_transaction_amount'])} | {money(x['median_transaction_amount'])} | "
        f"{x['spending_share_percentage']:.2f} % | {x['recent_direction']} |" for x in dev["category_metrics"])
    pattern_text = "\n\n".join(f"### {x['id']} - {x['name']}\n\n- Métrica: `{x['metric']}` = `{x['value']}`.\n"
        f"- Período: {x['period']}.\n- Interpretación: {x['interpretation']}\n- Limitación: {x['limitation']}"
        for x in data["selected_patterns"])
    examples = "\n".join(f"- Anterior ({x['previous_period']}) → actual ({x['current_period']}): {money(x['previous_spend'])} → "
        f"{money(x['current_spend'])}; asociación principal: **{x['main_association']}**; transacciones "
        f"{x['previous_transactions']} → {x['current_transactions']}; monto medio "
        f"{money(x['previous_average_transaction'])} → {money(x['current_average_transaction'])}."
        for x in dev["spending_increase_decomposition_examples"])
    audit = data["m_plus_one_viability_audit"]
    return f"""# Análisis ampliado de patrones habituales de consumo

## Alcance temporal

El dataset contiene {data['dataset_structure']['total_transactions']} gastos simulados entre {data['dataset_structure']['start_date']} y {data['dataset_structure']['end_date']} ({data['dataset_structure']['total_months']} meses). Patrones y variables candidatas usan exclusivamente {dev['transactions']} transacciones de 2024-01 a 2025-12. La reserva 2026-01 a 2026-06 no se utilizó para seleccionar variables, ajustar umbrales, comparar modelos ni evaluar rendimiento predictivo.

## Métricas generales de desarrollo

- Gasto total: **{money(general['spend'])}**; transacciones: **{general['transactions']}**.
- Gasto promedio diario: **{money(general['average_daily_spend'])}**.
- Promedio / mediana / máximo por transacción: **{money(general['average_transaction_amount'])} / {money(general['median_transaction_amount'])} / {money(general['max_transaction_amount'])}**.
- Días con gasto / sin gasto: **{general['active_spending_days']} / {general['inactive_spending_days']}**.
- Transacciones por día calendario / día activo: **{general['transactions_per_calendar_day']:.4f} / {general['transactions_per_active_day']:.4f}**.

## Ventanas, ritmo y correlación

- Corte {recent['cutoff_date']}: últimos 14 días {money(recent['last_14_days']['spend'])} y {recent['last_14_days']['transactions']} transacciones.
- Siete días anteriores → últimos 7 días, gasto: {money(recent['previous_7_days']['spend'])} → {money(recent['last_7_days']['spend'])}; variación {recent['changes_last_7_vs_previous_7']['spend']['percentage']} %.
- Siete días anteriores → últimos 7 días, transacciones: {recent['previous_7_days']['transactions']} → {recent['last_7_days']['transactions']}; variación {recent['changes_last_7_vs_previous_7']['transactions']['percentage']} %.
- Siete días anteriores → últimos 7 días, monto promedio: {money(recent['previous_7_days']['average_transaction_amount'])} → {money(recent['last_7_days']['average_transaction_amount'])}; variación {recent['changes_last_7_vs_previous_7']['average_transaction_amount']['percentage']} %.
- Primer 50 % vs segundo 50 %: **{dev['trend_signals']['direction']}**. Umbrales: {dev['trend_signals']['thresholds']}.
- Pendiente acumulada: {money(dev['trend_signals']['cumulative_spend_slope_per_day'])} diarios.
- Pearson: **{corr['pearson']:.6f}**; Spearman: **{corr['spearman']:.6f}**; observaciones: **{corr['observations']} días**.

**Una correlación estadística no permite establecer causalidad.** Los resultados muestran correlación/asociación y no demuestran causalidad.

## Descomposición de aumentos

{examples}

La descomposición usa gasto = frecuencia × monto medio y no constituye recomendación financiera.

## Comparación mensual equivalente

- Anterior: **{previous['previous_equivalent_period']}**.
- Actual: **{previous['current_period']}**.
- Gasto anterior → actual: {money(previous['previous']['spend'])} → {money(previous['current']['spend'])}; variación {previous['changes']['spend']['percentage']} %.
- Transacciones anteriores → actuales: {previous['previous']['transactions']} → {previous['current']['transactions']}; variación {previous['changes']['transactions']['percentage']} %.
- Promedio diario anterior → actual: {money(previous['previous']['average_daily_spend'])} → {money(previous['current']['average_daily_spend'])}; variación {previous['changes']['average_daily_spend']['percentage']} %.

Se comparan {previous['equivalent_days']} días en cada período; no se compara un mes parcial con uno completo.

## Categorías

| Categoría | Gasto | Transacciones | Promedio | Mediana | Participación | Ritmo reciente |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
{category_rows}

El JSON incluye ventanas, cambio, frecuencia, recencia, peso histórico, variabilidad y comparación mensual equivalente por categoría.

## Patrones definitivos

{pattern_text}

## Variables candidatas para T40

{', '.join(f'`{x}`' for x in CANDIDATES)}.

Disponibilidad buena en desarrollo. Redundancias: gasto 7 días con su tasa diaria; gasto 14 días con dos ventanas de 7; `category_share` con peso histórico. Frecuencia, estadísticas de monto, recencia, comparación mensual, categoría y pendiente aportan señales conceptualmente distintas. T39 no incorpora variables ni decide un modelo.

## Auditoría M→M+1

- Meses consecutivos: **{audit['consecutive_months']}**; transiciones globales: **{audit['global_transitions']}**; pares categoría-transición: **{audit['potential_category_month_pairs']}**.
- Desarrollo: **{audit['development_transitions']}** transiciones. División posible: objetivos 2024-02 a 2025-06 para desarrollo, 2025-07 a 2025-12 para validación y 2026-01 a 2026-06 reservados para el Ítem 22.
- Es una auditoría de viabilidad; no se entrenó un modelo M+1. La cantidad de transiciones independientes es limitada.

## Limitaciones

Datos simulados, ventanas sensibles a gastos puntuales, asociaciones sin causalidad y sin recomendaciones financieras.
"""


def main():
    all_rows = load(); start, end = all_rows[0]["date"], all_rows[-1]["date"]
    periods = months(start, end); dev_rows = [x for x in all_rows if x["date"] <= DEV_END]
    holdout = [x for x in all_rows if x["date"] >= HOLDOUT_START]
    daily = daily_series(dev_rows, start, DEV_END); general = aggregate(dev_rows)
    active = sum(x["daily_transaction_count"] > 0 for x in daily)
    general.update({"calendar_days": len(daily), "average_daily_spend": rnd(general["spend"]/len(daily)),
                    "active_spending_days": active, "inactive_spending_days": len(daily)-active,
                    "transactions_per_calendar_day": rnd(len(dev_rows)/len(daily), 4),
                    "transactions_per_active_day": rnd(len(dev_rows)/active, 4)})
    counts, spends = [x["daily_transaction_count"] for x in daily], [x["daily_spend"] for x in daily]
    corr = {"variables": ["daily_transaction_count", "daily_spend"], "observations": len(daily),
            "pearson": pearson(counts, spends), "spearman": pearson(ranks(counts), ranks(spends)),
            "interpretation": "asociación estadística descriptiva; no implica causalidad"}
    recent, rhythm = windows(dev_rows, DEV_END), trend(dev_rows, DEV_END)
    category_metrics = categories(dev_rows, DEV_END, general["spend"])
    period = f"{start} a {DEV_END}"
    data = {"dataset_structure": {"start_date": start.isoformat(), "end_date": end.isoformat(),
            "total_months": len(periods), "total_transactions": len(all_rows),
            "total_spend": rnd(sum(x["amount"] for x in all_rows))},
        "temporal_separation": {"development_period": period, "reserved_item_22_period": "2026-01-01 a 2026-06-30",
            "development_transactions": len(dev_rows), "reserved_transactions": len(holdout),
            "reserved_period_used_for_variable_selection": False,
            "reserved_period_use": "conteo estructural de meses y transiciones exclusivamente"},
        "development_analysis": {"period": period, "transactions": len(dev_rows), "general_metrics": general,
            "recent_windows": recent, "daily_frequency_spend_correlation": corr,
            "spending_increase_decomposition_examples": decompositions(dev_rows),
            "previous_month_equivalent_comparison": previous_month(dev_rows, DEV_END),
            "trend_signals": rhythm, "category_metrics": category_metrics},
        "selected_patterns": patterns(category_metrics, corr, recent, rhythm, period),
        "candidate_variables": {"variables": CANDIDATES, "availability": "sin información futura",
            "redundancies": ["spend_last_7_days ↔ recent_daily_spend_rate",
                             "spend_last_14_days ↔ dos ventanas de 7 días", "category_share ↔ peso histórico"]},
        "m_plus_one_viability_audit": {"consecutive_months": len(periods), "global_transitions": len(periods)-1,
            "potential_category_month_pairs": (len(periods)-1)*len(CATEGORIES),
            "development_transitions": len([x for x in periods if x <= "2025-12"])-1,
            "proposed_temporal_split": {"training_targets": "2024-02 a 2025-06 (17)",
                "validation_targets": "2025-07 a 2025-12 (6)", "reserved_targets": "2026-01 a 2026-06 (6)"},
            "limitations": ["29 transiciones globales por categoría", "sin entrenamiento M+1"]},
        "causality_statement": "Los resultados muestran correlación/asociación y no demuestran causalidad."}
    if len(category_metrics) != 10 or [x["date"] for x in daily] != sorted(x["date"] for x in daily):
        raise ValueError("Validación de categorías u orden temporal fallida.")
    encoded = json.dumps(data, ensure_ascii=False)
    if any(token in encoded for token in ["NaN", "Infinity", "-Infinity"]):
        raise ValueError("Resultado no finito.")
    OUT.mkdir(parents=True, exist_ok=True)
    with DAILY.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(daily[0])); writer.writeheader(); writer.writerows(daily)
    with SUMMARY.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")
    REPORT.write_text(build_report(data), encoding="utf-8", newline="\n")
    print(f"T39 generado: {len(all_rows)} totales, {len(dev_rows)} de desarrollo, {len(daily)} días.")


if __name__ == "__main__":
    main()
