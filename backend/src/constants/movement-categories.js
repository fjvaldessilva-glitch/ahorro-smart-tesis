const incomeCategories = Object.freeze([
  'Sueldo',
  'Otros ingresos',
])

const expenseCategories = Object.freeze([
  'Alimentación',
  'Transporte',
  'Vivienda',
  'Servicios básicos',
  'Salud',
  'Educación',
  'Pago de deudas y créditos',
  'Entretenimiento',
  'Mascotas',
  'Otros gastos',
])

const categoriesByType = Object.freeze({
  Ingreso: incomeCategories,
  Gasto: expenseCategories,
})

const movementTypes = Object.freeze(Object.keys(categoriesByType))
const movementCategories = Object.freeze([
  ...incomeCategories,
  ...expenseCategories,
])

module.exports = {
  categoriesByType,
  expenseCategories,
  movementCategories,
  movementTypes,
}
