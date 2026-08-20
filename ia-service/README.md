# Ahorro Smart - Servicio predictivo

Servicio FastAPI independiente que utiliza el modelo de T40 para proyectar el gasto total esperado al cierre del mes en curso a partir de la actividad registrada hasta una fecha de corte.

## Requisitos

- Python 3.13 o compatible.
- Dependencias declaradas en `requirements.txt`.
- Artefactos `models/month_end_forecast_model.joblib` y `models/month_end_model_metadata.json`.

## Ejecución

Desde `ia-service`:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La documentación interactiva queda disponible en `http://127.0.0.1:8000/docs`.

## GET /health

Informa la disponibilidad del servicio, el modelo cargado, su objetivo predictivo y la versión de Scikit-learn registrada en los metadatos.

## POST /predict

Recibe `cutoff_date` y los gastos disponibles hasta esa fecha. La actividad parcial del mismo mes es la fuente principal de la proyección; el mes inmediatamente anterior se utiliza como señal opcional cuando está disponible.

```json
{
  "cutoff_date": "2026-08-19",
  "expenses": [
    {"date": "2026-08-03", "category": "Alimentación", "amount": 25000}
  ]
}
```

Debe existir al menos un gasto válido entre el primer día del mes y `cutoff_date`. No se exigen meses anteriores y se rechazan movimientos posteriores al corte.

La respuesta incluye:

- Período proyectado, correspondiente al mismo mes de `cutoff_date`.
- Diez proyecciones por categoría y total proyectado.
- `spent_to_date`, calculado exclusivamente con el mes en curso.
- `previous_month_total` y `has_previous_month_data`.
- Cantidad de gastos del mes actual utilizados.
- Modelo, objetivo y valores brutos antes del ajuste de no negatividad.

Si una predicción es negativa, se conserva en `raw_prediction` y se publica `projected_amount=max(0, raw_prediction)`.

## Modelo utilizado

El servicio carga `month_end_forecast_model.joblib`, un pipeline `LinearRegression` entrenado con datos completamente simulados. Puede producir una estimación desde el primer mes con un gasto válido. El historial anterior es opcional.

El presupuesto mensual no se recibe ni se utiliza como variable predictiva. El sistema principal podrá comparar posteriormente la proyección con el presupuesto y calcular la desviación esperada.

## Limitaciones

Las proyecciones son académicas e informativas y no constituyen asesoría financiera. El desempeño con datos reales puede diferir del escenario sintético controlado. Los meses 2026-01 a 2026-06 permanecen reservados para la evaluación formal del Ítem 22.
