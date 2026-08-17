const express = require('express')
const authenticateToken = require('../middleware/auth.middleware')
const Budget = require('../models/Budget')

const router = express.Router()

router.use(express.json())
router.use(authenticateToken)

const getPublicBudget = (budget) => ({
  id: budget._id.toString(),
  amount: budget.amount,
})

router.get('/', async (request, response) => {
  try {
    const budget = await Budget.findOne({
      user: request.authenticatedUserId,
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
  const amount = Number(request.body?.amount)

  if (!Number.isFinite(amount) || amount <= 0) {
    return response.status(400).json({
      status: 'error',
      message: 'El presupuesto debe ser un monto mayor que cero.',
    })
  }

  try {
    const budget = await Budget.findOneAndUpdate(
      { user: request.authenticatedUserId },
      {
        $set: { amount },
        $setOnInsert: { user: request.authenticatedUserId },
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
