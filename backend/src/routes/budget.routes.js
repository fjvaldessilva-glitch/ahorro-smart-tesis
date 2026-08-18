const express = require('express')
const authenticateToken = require('../middleware/auth.middleware')
const Budget = require('../models/Budget')

const router = express.Router()

router.use(express.json())
router.use(authenticateToken)

const getPublicBudget = (budget) => ({
  id: budget._id.toString(),
  year: budget.year,
  month: budget.month,
  amount: budget.amount,
})

const getValidatedPeriod = (yearValue, monthValue) => {
  const year = Number(yearValue)
  const month = Number(monthValue)

  if (!Number.isInteger(year) || year <= 0) {
    return { error: 'El año del presupuesto no es válido.' }
  }

  if (!Number.isInteger(month) || month < 1 || month > 12) {
    return { error: 'El mes del presupuesto debe estar entre 1 y 12.' }
  }

  return { year, month }
}

router.get('/', async (request, response) => {
  const { year, month, error } = getValidatedPeriod(
    request.query.year,
    request.query.month,
  )

  if (error) {
    return response.status(400).json({
      status: 'error',
      message: error,
    })
  }

  try {
    const budget = await Budget.findOne({
      user: request.authenticatedUserId,
      year,
      month,
    })

    return response.json({
      budget: budget ? getPublicBudget(budget) : null,
    })
  } catch (error) {
    console.error(`Error al consultar presupuesto: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible consultar el presupuesto.',
    })
  }
})

router.put('/', async (request, response) => {
  const { year, month, error } = getValidatedPeriod(
    request.body?.year,
    request.body?.month,
  )
  const amount = Number(request.body?.amount)

  if (error) {
    return response.status(400).json({
      status: 'error',
      message: error,
    })
  }

  if (!Number.isFinite(amount) || amount <= 0) {
    return response.status(400).json({
      status: 'error',
      message: 'El presupuesto debe ser un monto mayor que cero.',
    })
  }

  try {
    const budget = await Budget.findOneAndUpdate(
      {
        user: request.authenticatedUserId,
        year,
        month,
      },
      {
        $set: { amount },
        $setOnInsert: {
          user: request.authenticatedUserId,
          year,
          month,
        },
      },
      {
        upsert: true,
        returnDocument: 'after',
        runValidators: true,
      },
    )

    return response.json({
      status: 'ok',
      budget: getPublicBudget(budget),
    })
  } catch (error) {
    console.error(`Error al guardar presupuesto: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible guardar el presupuesto.',
    })
  }
})

module.exports = router
