const express = require('express')
const mongoose = require('mongoose')
const authenticateToken = require('../middleware/auth.middleware')
const Movement = require('../models/Movement')
const { categoriesByType } = require('../constants/movement-categories')

const router = express.Router()

const descriptionLetterPattern = /\p{L}/u

router.use(express.json())
router.use(authenticateToken)

const getValidatedMovementData = (body = {}) => {
  const description = String(body.description ?? '').trim()
  const category = String(body.category ?? '').trim()
  const type = String(body.type ?? '').trim()
  const amount = Number(body.amount)
  const date = String(body.date ?? '').trim()

  if (!descriptionLetterPattern.test(description)) {
    return {
      error: 'La descripción debe contener al menos una letra.',
    }
  }

  const allowedCategories = categoriesByType[type]
  const hasRequiredFields = category && type && date
  const hasValidAmount = Number.isFinite(amount) && amount > 0
  const hasCompatibleCategory = allowedCategories?.includes(category) ?? false

  if (!hasRequiredFields || !hasValidAmount || !hasCompatibleCategory) {
    return {
      error: 'Datos de movimiento inválidos',
    }
  }

  return {
    movementData: {
      descripcion: description,
      categoria: category,
      tipo: type,
      monto: amount,
      fecha: date,
    },
  }
}

const getPublicMovement = (movement) => ({
  id: movement._id.toString(),
  description: movement.descripcion,
  category: movement.categoria,
  type: movement.tipo,
  amount: movement.monto,
  date: movement.fecha,
})

const isValidMovementId = (id) => mongoose.isObjectIdOrHexString(id)

router.get('/', async (request, response) => {
  try {
    const movements = await Movement.find({
      user: request.authenticatedUserId,
    }).sort({ createdAt: 1 })

    return response.json(movements.map(getPublicMovement))
  } catch (error) {
    console.error(`Error al consultar movimientos: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible consultar los movimientos.',
    })
  }
})

router.post('/', async (request, response) => {
  const { movementData, error } = getValidatedMovementData(request.body)

  if (error) {
    return response.status(400).json({
      status: 'error',
      message: error,
    })
  }

  try {
    const movement = await Movement.create({
      user: request.authenticatedUserId,
      ...movementData,
    })

    return response.status(201).json(getPublicMovement(movement))
  } catch (creationError) {
    console.error(`Error al crear movimiento: ${creationError.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible crear el movimiento.',
    })
  }
})

router.put('/:id', async (request, response) => {
  if (!isValidMovementId(request.params.id)) {
    return response.status(404).json({
      status: 'error',
      message: 'Movimiento no encontrado',
    })
  }

  const { movementData, error } = getValidatedMovementData(request.body)

  if (error) {
    return response.status(400).json({
      status: 'error',
      message: error,
    })
  }

  try {
    const movement = await Movement.findOneAndUpdate(
      {
        _id: request.params.id,
        user: request.authenticatedUserId,
      },
      { $set: movementData },
      { returnDocument: 'after', runValidators: true },
    )

    if (!movement) {
      return response.status(404).json({
        status: 'error',
        message: 'Movimiento no encontrado',
      })
    }

    return response.json(getPublicMovement(movement))
  } catch (updateError) {
    console.error(`Error al editar movimiento: ${updateError.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible editar el movimiento.',
    })
  }
})

router.delete('/:id', async (request, response) => {
  if (!isValidMovementId(request.params.id)) {
    return response.status(404).json({
      status: 'error',
      message: 'Movimiento no encontrado',
    })
  }

  try {
    const movement = await Movement.findOneAndDelete({
      _id: request.params.id,
      user: request.authenticatedUserId,
    })

    if (!movement) {
      return response.status(404).json({
        status: 'error',
        message: 'Movimiento no encontrado',
      })
    }

    return response.json({
      status: 'ok',
      message: 'Movimiento eliminado',
      id: movement._id.toString(),
    })
  } catch (deletionError) {
    console.error(`Error al eliminar movimiento: ${deletionError.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible eliminar el movimiento.',
    })
  }
})

module.exports = router
