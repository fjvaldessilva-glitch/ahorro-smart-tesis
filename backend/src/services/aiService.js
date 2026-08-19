const { expenseCategories } = require('../constants/movement-categories')

const DEFAULT_IA_SERVICE_URL = 'http://127.0.0.1:8000'
const REQUEST_TIMEOUT_MS = 10000

class AiServiceError extends Error {
  constructor(message, statusCode = 502) {
    super(message)
    this.name = 'AiServiceError'
    this.statusCode = statusCode
  }
}

const getPredictUrl = () => {
  const baseUrl = String(process.env.IA_SERVICE_URL || DEFAULT_IA_SERVICE_URL).replace(/\/$/, '')
  return `${baseUrl}/predict`
}

const getErrorMessage = (status, body) => {
  if (status === 400 || status === 422) {
    const detail = typeof body?.detail === 'string' ? body.detail : ''
    if (/tres meses|historial/i.test(detail)) {
      return 'No existe historial suficiente para generar la proyección.'
    }
    return 'El historial financiero no permite generar la proyección solicitada.'
  }
  return 'El servicio predictivo no pudo generar la proyección.'
}

const validatePredictionResponse = (prediction, targetPeriod) => {
  const categories = prediction?.categories
  const receivedCategories = Array.isArray(categories)
    ? categories.map(({ category }) => category)
    : []
  const hasOfficialCategories = categories?.length === expenseCategories.length
    && new Set(receivedCategories).size === expenseCategories.length
    && expenseCategories.every((category) => receivedCategories.includes(category))
  const hasValidAmounts = categories?.every((item) => (
    Number.isFinite(item.projected_amount)
      && item.projected_amount >= 0
      && Number.isFinite(item.raw_prediction)
      && typeof item.nonnegative_adjustment === 'boolean'
  ))

  if (
    prediction?.target_period !== targetPeriod
    || typeof prediction?.model_name !== 'string'
    || !prediction.model_name.trim()
    || !hasOfficialCategories
    || !hasValidAmounts
    || !Number.isFinite(prediction?.total_projected_amount)
    || prediction.total_projected_amount < 0
    || !Number.isInteger(prediction?.historical_months_used)
    || prediction.historical_months_used < 3
  ) {
    throw new AiServiceError('El servicio predictivo devolvió una respuesta inválida.')
  }

  return prediction
}

const requestPrediction = async (payload) => {
  const abortController = new AbortController()
  const timeout = setTimeout(() => abortController.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(getPredictUrl(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: abortController.signal,
    })
    let body
    try {
      body = await response.json()
    } catch (_error) {
      throw new AiServiceError('El servicio predictivo devolvió una respuesta inválida.')
    }

    if (!response.ok) {
      const statusCode = response.status === 400 || response.status === 422 ? 400 : 502
      throw new AiServiceError(getErrorMessage(response.status, body), statusCode)
    }

    return validatePredictionResponse(body, payload.target_period)
  } catch (error) {
    if (error instanceof AiServiceError) {
      throw error
    }
    const message = error?.name === 'AbortError'
      ? 'El servicio predictivo excedió el tiempo de espera.'
      : 'El servicio predictivo no está disponible.'
    throw new AiServiceError(message)
  } finally {
    clearTimeout(timeout)
  }
}

module.exports = {
  AiServiceError,
  requestPrediction,
}
