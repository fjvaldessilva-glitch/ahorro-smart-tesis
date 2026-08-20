const Movement = require('../models/Movement')
const Projection = require('../models/Projection')
const { expenseCategories } = require('../constants/movement-categories')
const { AiServiceError, requestPrediction } = require('../services/aiService')

const periodPattern = /^\d{4}-(0[1-9]|1[0-2])$/
const isoDatePattern = /^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$/

const isValidIsoDate = (value) => {
  if (!isoDatePattern.test(value)) return false
  const parsed = new Date(`${value}T00:00:00.000Z`)
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value
}

const validateCutoffDate = (value) => {
  const cutoffDate = String(value ?? '').trim()
  return isValidIsoDate(cutoffDate) ? cutoffDate : null
}

const validateProjectedPeriod = (value) => {
  const projectedPeriod = String(value ?? '').trim()
  return periodPattern.test(projectedPeriod) ? projectedPeriod : null
}

const shiftPeriod = (period, offset) => {
  const [year, month] = period.split('-').map(Number)
  const absoluteMonth = year * 12 + month - 1 + offset
  return `${Math.floor(absoluteMonth / 12).toString().padStart(4, '0')}-${String((absoluteMonth % 12) + 1).padStart(2, '0')}`
}

const getPublicProjection = (projection) => ({
  id: projection._id.toString(),
  cutoffDate: projection.cutoffDate,
  projectedPeriod: projection.targetPeriod,
  modelName: projection.modelName,
  predictionObjective: projection.predictionObjective,
  categories: projection.categories.map((item) => ({
    category: item.category,
    projectedAmount: item.projectedAmount,
    rawPrediction: item.rawPrediction,
    nonnegativeAdjustment: item.nonnegativeAdjustment,
  })),
  spentToDate: projection.spentToDate,
  totalProjectedAmount: projection.totalProjectedAmount,
  previousMonthTotal: projection.previousMonthTotal,
  hasPreviousMonthData: projection.hasPreviousMonthData,
  currentMonthExpensesUsed: projection.currentMonthExpensesUsed,
  generatedAt: projection.generatedAt,
})

const getPredictionExpenses = async (userId, cutoffDate) => {
  const projectedPeriod = cutoffDate.slice(0, 7)
  const previousPeriod = shiftPeriod(projectedPeriod, -1)
  const movements = await Movement.find({
    user: userId,
    tipo: 'Gasto',
    fecha: {
      $gte: `${previousPeriod}-01`,
      $lte: cutoffDate,
    },
  }).select('categoria monto fecha').sort({ fecha: 1 })

  const hasInvalidMovement = movements.some((movement) => (
    !expenseCategories.includes(movement.categoria)
      || !Number.isFinite(movement.monto)
      || movement.monto <= 0
      || !isValidIsoDate(movement.fecha)
  ))
  if (hasInvalidMovement) {
    return { error: 'Los movimientos de gasto disponibles contienen datos inválidos.' }
  }

  const currentMonthExpenses = movements.filter((movement) => (
    movement.fecha.startsWith(projectedPeriod)
  ))
  if (currentMonthExpenses.length === 0) {
    return {
      error: 'No existen gastos registrados en el mes en curso para generar una proyección.',
    }
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
  const cutoffDate = validateCutoffDate(request.body?.cutoffDate)
  if (!cutoffDate) {
    return response.status(400).json({
      status: 'error',
      message: 'La fecha de corte debe utilizar el formato YYYY-MM-DD y ser válida.',
    })
  }

  try {
    const { expenses, error } = await getPredictionExpenses(
      request.authenticatedUserId,
      cutoffDate,
    )
    if (error) {
      return response.status(422).json({ status: 'error', message: error })
    }

    const prediction = await requestPrediction({
      cutoff_date: cutoffDate,
      expenses,
    })
    const targetPeriod = prediction.projected_period
    const generatedAt = new Date()
    const projectionData = {
      cutoffDate: prediction.cutoff_date,
      modelName: prediction.model_name,
      predictionObjective: prediction.prediction_objective,
      categories: prediction.categories.map((item) => ({
        category: item.category,
        projectedAmount: item.projected_amount,
        rawPrediction: item.raw_prediction,
        nonnegativeAdjustment: item.nonnegative_adjustment,
      })),
      spentToDate: prediction.spent_to_date,
      totalProjectedAmount: prediction.total_projected_amount,
      previousMonthTotal: prediction.previous_month_total,
      hasPreviousMonthData: prediction.has_previous_month_data,
      currentMonthExpensesUsed: prediction.current_month_expenses_used,
      generatedAt,
    }
    const projection = await Projection.findOneAndUpdate(
      { user: request.authenticatedUserId, targetPeriod },
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
  const projectedPeriod = validateProjectedPeriod(request.query.projectedPeriod)
  if (!projectedPeriod) {
    return response.status(400).json({
      status: 'error',
      message: 'El período proyectado debe utilizar el formato YYYY-MM.',
    })
  }

  try {
    const projection = await Projection.findOne({
      user: request.authenticatedUserId,
      targetPeriod: projectedPeriod,
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
