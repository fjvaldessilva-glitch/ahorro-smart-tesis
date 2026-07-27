const express = require('express')

const router = express.Router()

const categoriesByType = {
  Ingreso: ['Sueldo', 'Otros ingresos'],
  Gasto: [
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
  ],
}

const movements = []
let nextMovementId = 1

router.use(express.json())

router.get('/', (_request, response) => {
  response.json(movements)
})

router.post('/', (request, response) => {
  const description = String(request.body.description ?? '').trim()
  const category = String(request.body.category ?? '').trim()
  const type = String(request.body.type ?? '').trim()
  const amount = Number(request.body.amount)
  const date = String(request.body.date ?? '').trim()

  const allowedCategories = categoriesByType[type]
  const hasRequiredFields = description && category && type && date
  const hasValidAmount = Number.isFinite(amount) && amount > 0
  const hasCompatibleCategory = allowedCategories?.includes(category) ?? false

  if (!hasRequiredFields || !hasValidAmount || !hasCompatibleCategory) {
    return response.status(400).json({
      status: 'error',
      message: 'Datos de movimiento inválidos',
    })
  }

  const movement = {
    id: nextMovementId,
    description,
    category,
    type,
    amount,
    date,
  }

  nextMovementId += 1
  movements.push(movement)

  return response.status(201).json(movement)
})

module.exports = router
