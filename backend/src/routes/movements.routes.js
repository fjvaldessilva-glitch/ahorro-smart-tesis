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

const getValidatedMovementData = (body = {}) => {
  const description = String(body.description ?? '').trim()
  const category = String(body.category ?? '').trim()
  const type = String(body.type ?? '').trim()
  const amount = Number(body.amount)
  const date = String(body.date ?? '').trim()

  const allowedCategories = categoriesByType[type]
  const hasRequiredFields = description && category && type && date
  const hasValidAmount = Number.isFinite(amount) && amount > 0
  const hasCompatibleCategory = allowedCategories?.includes(category) ?? false

  if (!hasRequiredFields || !hasValidAmount || !hasCompatibleCategory) {
    return null
  }

  return {
    description,
    category,
    type,
    amount,
    date,
  }
}

router.get('/', (_request, response) => {
  response.json(movements)
})

router.post('/', (request, response) => {
  const movementData = getValidatedMovementData(request.body)

  if (!movementData) {
    return response.status(400).json({
      status: 'error',
      message: 'Datos de movimiento inválidos',
    })
  }

  const movement = {
    id: nextMovementId,
    ...movementData,
  }

  nextMovementId += 1
  movements.push(movement)

  return response.status(201).json(movement)
})

router.put('/:id', (request, response) => {
  const movementId = Number(request.params.id)
  const movementIndex = movements.findIndex(
    (movement) => movement.id === movementId,
  )

  if (movementIndex === -1) {
    return response.status(404).json({
      status: 'error',
      message: 'Movimiento no encontrado',
    })
  }

  const movementData = getValidatedMovementData(request.body)

  if (!movementData) {
    return response.status(400).json({
      status: 'error',
      message: 'Datos de movimiento inválidos',
    })
  }

  const updatedMovement = {
    id: movementId,
    ...movementData,
  }

  movements[movementIndex] = updatedMovement

  return response.json(updatedMovement)
})

router.delete('/:id', (request, response) => {
  const movementId = Number(request.params.id)
  const movementIndex = movements.findIndex(
    (movement) => movement.id === movementId,
  )

  if (movementIndex === -1) {
    return response.status(404).json({
      status: 'error',
      message: 'Movimiento no encontrado',
    })
  }

  const [deletedMovement] = movements.splice(movementIndex, 1)

  return response.json({
    status: 'ok',
    message: 'Movimiento eliminado',
    id: deletedMovement.id,
  })
})

module.exports = router
