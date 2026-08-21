# Optimización selectiva de variables B3 — T40.3.4

## Alcance

Se compararon A, B3, C1, C2, C3 y C4 mediante `LinearRegression`, `OneHotEncoder(handle_unknown="ignore")`, las mismas filas y el target `category_month_end_total`. El entrenamiento corresponde a 2024-01–2025-06 y la validación a 2025-07–2025-12. La reserva 2026-01–2026-06 fue excluida.

## Resultados globales

| Variante | MAE | RMSE | WAPE | Negativas | Desv. WAPE mensual | Meses mejorados | Aceptada |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 54894.3302 | 67676.8420 | 4.1554 % | 8 | 2.6212 | — | Referencia |
| B3 | 52647.3167 | 66351.6913 | 3.9853 % | 2 | 2.4838 | 5 | False |
| C1 | 53140.3013 | 66662.9610 | 4.0226 % | 8 | 2.5916 | 5 | False |
| C2 | 58405.1602 | 70515.8080 | 4.4211 % | 0 | 1.6057 | 2 | False |
| C3 | 52803.1442 | 66018.5863 | 3.9971 % | 2 | 2.4975 | 5 | False |
| C4 | 52630.2834 | 65779.1953 | 3.9840 % | 2 | 2.5821 | 3 | False |

## WAPE mensual y diferencia contra A

Los valores entre paréntesis corresponden a la diferencia en puntos frente a A; un valor negativo representa mejora.

| Mes | A | B3 | C1 | C2 | C3 | C4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-07 | 7.1161 | 6.9970 (-0.1191) | 6.6188 (-0.4973) | 4.8941 (-2.2220) | 6.6916 (-0.4245) | 6.2284 (-0.8877) |
| 2025-08 | 3.1839 | 3.0790 (-0.1049) | 3.1599 (-0.0240) | 4.7012 (+1.5173) | 3.1522 (-0.0317) | 3.2905 (+0.1066) |
| 2025-09 | 1.1850 | 1.3920 (+0.2070) | 1.1299 (-0.0551) | 2.6878 (+1.5028) | 1.2620 (+0.0770) | 1.5793 (+0.3943) |
| 2025-10 | 4.7907 | 4.4870 (-0.3037) | 4.8271 (+0.0364) | 4.8595 (+0.0688) | 4.7806 (-0.0101) | 4.3249 (-0.4658) |
| 2025-11 | 1.1766 | 0.9661 (-0.2105) | 0.9422 (-0.2344) | 2.4262 (+1.2496) | 0.9465 (-0.2301) | 0.7013 (-0.4753) |
| 2025-12 | 7.8204 | 7.3092 (-0.5112) | 7.8081 (-0.0123) | 7.2506 (-0.5698) | 7.4711 (-0.3493) | 8.2080 (+0.3876) |

## WAPE por categoría

| Categoría | A | B3 | C1 | C2 | C3 | C4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Alimentación | 23.4052 | 24.1394 | 23.4355 | 24.3037 | 24.1184 | 24.0546 |
| Transporte | 32.3167 | 27.1408 | 32.3018 | 27.4640 | 27.1491 | 27.2433 |
| Vivienda | 6.4619 | 3.3451 | 6.4352 | 3.2762 | 3.3188 | 3.3076 |
| Servicios básicos | 14.5566 | 10.0471 | 14.4900 | 9.8174 | 9.9384 | 10.0717 |
| Salud | 141.3322 | 144.6224 | 140.8489 | 142.3012 | 144.9048 | 145.8517 |
| Educación | 112.1973 | 113.0225 | 113.5808 | 117.3917 | 113.2754 | 113.9931 |
| Pago de deudas y créditos | 11.6212 | 7.4081 | 11.6953 | 7.6476 | 7.4321 | 7.4477 |
| Entretenimiento | 51.6977 | 54.1391 | 51.5478 | 51.7366 | 54.0268 | 53.8698 |
| Mascotas | 60.6442 | 64.3819 | 60.9147 | 63.3526 | 64.5080 | 66.9609 |
| Otros gastos | 114.1244 | 99.3388 | 113.3584 | 97.7588 | 99.6073 | 100.3474 |

## WAPE por fecha de corte

| Corte | A | B3 | C1 | C2 | C3 | C4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| first_expense_day | 4.0280 | 4.0183 | 3.9678 | 4.2671 | 3.9766 | 3.3248 |
| day_5 | 4.3965 | 3.7759 | 3.9129 | 2.7418 | 3.9144 | 4.1127 |
| day_10 | 4.5278 | 4.1963 | 4.1626 | 5.0254 | 4.1763 | 4.5676 |
| day_15 | 3.9776 | 4.3130 | 4.3406 | 5.6376 | 4.2892 | 4.1547 |
| day_20 | 4.2144 | 4.3592 | 4.2562 | 5.4636 | 4.2497 | 4.1209 |
| day_25 | 3.7879 | 3.2490 | 3.4954 | 3.3913 | 3.3762 | 3.6232 |

## Comparación con A

### B3

- Mejora absoluta de WAPE: +0.1701 puntos.
- Mejora relativa de WAPE: +4.0935 %.
- Cambio de MAE / RMSE: -4.0933 % / -1.9581 %.
- Meses mejorados / empeorados: 5 / 1.
- Deterioros graves en categorías pequeñas: ninguno.
- Aceptada: **No**.
### C1

- Mejora absoluta de WAPE: +0.1328 puntos.
- Mejora relativa de WAPE: +3.1958 %.
- Cambio de MAE / RMSE: -3.1953 % / -1.4981 %.
- Meses mejorados / empeorados: 5 / 1.
- Deterioros graves en categorías pequeñas: ninguno.
- Aceptada: **No**.
### C2

- Mejora absoluta de WAPE: -0.2657 puntos.
- Mejora relativa de WAPE: -6.3941 %.
- Cambio de MAE / RMSE: +6.3956 % / +4.1949 %.
- Meses mejorados / empeorados: 2 / 4.
- Deterioros graves en categorías pequeñas: ninguno.
- Aceptada: **No**.
### C3

- Mejora absoluta de WAPE: +0.1583 puntos.
- Mejora relativa de WAPE: +3.8095 %.
- Cambio de MAE / RMSE: -3.8095 % / -2.4503 %.
- Meses mejorados / empeorados: 5 / 1.
- Deterioros graves en categorías pequeñas: ninguno.
- Aceptada: **No**.
### C4

- Mejora absoluta de WAPE: +0.1714 puntos.
- Mejora relativa de WAPE: +4.1248 %.
- Cambio de MAE / RMSE: -4.1244 % / -2.8040 %.
- Meses mejorados / empeorados: 3 / 3.
- Deterioros graves en categorías pequeñas: ninguno.
- Aceptada: **No**.

## Diagnóstico selectivo

- Mejor variante por WAPE: **C4**.
- Mejor variante por estabilidad mensual: **C2**.
- B3 conserva las tres variables originales y reproduce el WAPE 3,9853 % observado en T40.3.2.
- Al retirar `previous_month_comparable_transactions`, C3 cambia el WAPE en +0.0118 puntos respecto de B3. Por tanto, esta variable aporta una mejora pequeña al WAPE y no se considera redundante con evidencia suficiente para descartarla.
- C1 confirma que `previous_month_comparable_spend` aporta la principal señal monetaria global: mejora A, aunque no alcanza el desempeño de B3.
- C2 demuestra que `category_previous_month_comparable_spend` de forma aislada no mejora el baseline, pese a registrar la menor dispersión mensual.
- La combinación monetaria C3 cambia el WAPE en -0.0255 puntos respecto de C1, lo que indica un aporte complementario pequeño de la comparación por categoría.
- Al agregar `transactions_last_7_days` sobre C3, C4 cambia el WAPE en -0.0131 puntos. La mejora global es marginal y reduce de cinco a tres los meses mejorados frente a A, por lo que su aporte no es temporalmente consistente.
- Las variables monetarias comparables explican la mayor parte de la mejora observada; la frecuencia reciente no proporciona evidencia suficiente para una sustitución.

## Recomendación

Ninguna variante satisface simultáneamente todos los criterios; se mantiene A como referencia técnica.

Los modelos fueron entrenados exclusivamente en memoria. No se guardó ningún `.joblib`, no se reemplazó el baseline y FastAPI permaneció intacto.
