const Movement = require('../models/Movement')
const Projection = require('../models/Projection')
const { expenseCategories } = require('../constants/movement-categories')
const { AiServiceError, requestPrediction } = require('../services/aiService')

const targetPeriodPattern = /^\d{4}-(0[1-9]|1[0-2])$/
const isoDatePattern = /^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$/

const validateTargetPeriod = (value) => {
  const targetPeriod = String(value ?? '').trim()
  return targetPeriodPattern.test(targetPeriod) ? targetPeriod : null
}

const isValidIsoDate = (value) => {
  if (!isoDatePattern.test(value)) {
    return false
  }
  const parsed = new Date(`${value}T00:00:00.000Z`)
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value
}

const getPublicProjection = (projection) => ({
  id: projection._id.toString(),
  targetPeriod: projection.targetPeriod,
  modelName: projection.modelName,
  categories: projection.categories.map((item) => ({
    category: item.category,
    projectedAmount: item.projectedAmount,
    rawPrediction: item.rawPrediction,
    nonnegativeAdjustment: item.nonnegativeAdjustment,
  })),
  totalProjectedAmount: projection.totalProjectedAmount,
  historicalMonthsUsed: projection.historicalMonthsUsed,
  generatedAt: projection.generatedAt,
})

const getHistoricalExpenses = async (userId, targetPeriod) => {
  const movements = await Movement.find({
    user: userId,
    tipo: 'Gasto',
    fecha: { $lt: `${targetPeriod}-01` },
  }).select('categoria monto fecha').sort({ fecha: 1 })

  if (movements.length === 0) {
    return { error: 'El usuario no posee gastos históricos para generar una proyección.' }
  }

  const hasInvalidMovement = movements.some((movement) => (
    !expenseCategories.includes(movement.categoria)
      || !Number.isFinite(movement.monto)
      || movement.monto <= 0
      || !isValidIsoDate(movement.fecha)
  ))
  if (hasInvalidMovement) {
    return { error: 'El historial contiene movimientos de gasto inválidos.' }
  }

  return {
    expenses: movements.map((movement) => ({
      date: movement.fecha,
      category: movement.categoria,
      amount: movement.monto,
    })),
  }
}

const generateProjection = async (request, response) => {
  const targetPeriod = validateTargetPeriod(request.body?.targetPeriod)
  if (!targetPeriod) {
    return response.status(400).json({
      status: 'error',
      message: 'El período objetivo debe utilizar el formato YYYY-MM.',
    })
  }

  try {
    const { expenses, error } = await getHistoricalExpenses(
      request.authenticatedUserId,
      targetPeriod,
    )
    if (error) {
      return response.status(422).json({ status: 'error', message: error })
    }

    const prediction = await requestPrediction({
      target_period: targetPeriod,
      expenses,
    })
    const generatedAt = new Date()
    const projectionData = {
      modelName: prediction.model_name,
      categories: prediction.categories.map((item) => ({
        category: item.category,
        projectedAmount: item.projected_amount,
        rawPrediction: item.raw_prediction,
        nonnegativeAdjustment: item.nonnegative_adjustment,
      })),
      totalProjectedAmount: prediction.total_projected_amount,
      historicalMonthsUsed: prediction.historical_months_used,
      generatedAt,
    }
    const projection = await Projection.findOneAndUpdate(
      {
        user: request.authenticatedUserId,
        targetPeriod,
      },
      {
        $set: projectionData,
        $setOnInsert: {
          user: request.authenticatedUserId,
          targetPeriod,
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
      projection: getPublicProjection(projection),
    })
  } catch (error) {
    if (error instanceof AiServiceError) {
      return response.status(error.statusCode).json({
        status: 'error',
        message: error.message,
      })
    }
    console.error(`Error al generar proyección: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible generar la proyección.',
    })
  }
}

const getProjection = async (request, response) => {
  const targetPeriod = validateTargetPeriod(request.query.targetPeriod)
  if (!targetPeriod) {
    return response.status(400).json({
      status: 'error',
      message: 'El período objetivo debe utilizar el formato YYYY-MM.',
    })
  }

  try {
    const projection = await Projection.findOne({
      user: request.authenticatedUserId,
      targetPeriod,
    })
    if (!projection) {
      return response.status(404).json({
        status: 'error',
        message: 'Proyección no encontrada.',
      })
    }
    return response.json({
      status: 'ok',
      projection: getPublicProjection(projection),
    })
  } catch (error) {
    console.error(`Error al consultar proyección: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible consultar la proyección.',
    })
  }
}

module.exports = {
  generateProjection,
  getProjection,
}
