# Dataset simulado de gastos

Este directorio contiene datos **100 % simulados** para desarrollar y evaluar de forma controlada el componente predictivo de Ahorro Smart. No contiene información personal, bancaria ni financiera real y su uso es exclusivamente académico y de prueba.

- Período: 2024-01-01 a 2026-06-30 (30 meses completos).
- Semilla reproducible: `2026`.
- Variables originales: `date`, `category`, `amount` (fecha, categoría y monto del gasto).
- Variables derivadas: `year`, `month`, `period`, `monthly_amount`, `transaction_count`.
- Origen de las variables derivadas: se calculan únicamente desde la fecha, categoría y monto originales; los movimientos se agrupan por período mensual y categoría.
- Categorías: Alimentación, Transporte, Vivienda, Servicios básicos, Salud, Educación, Pago de deudas y créditos, Entretenimiento, Mascotas y Otros gastos.

Desde la raíz del repositorio, el dataset se regenera y procesa con:

```powershell
python ia-service/scripts/generate_simulated_data.py
python ia-service/scripts/preprocess_data.py
```

El procesamiento valida todos los registros antes de producir el archivo agregado y se detiene si encuentra datos inválidos.
