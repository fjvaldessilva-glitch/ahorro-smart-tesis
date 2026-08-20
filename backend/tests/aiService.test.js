const assert = require('node:assert/strict')
const { afterEach, test } = require('node:test')
const { AiServiceError, requestPrediction } = require('../src/services/aiService')
const { expenseCategories } = require('../src/constants/movement-categories')

const originalFetch = global.fetch
const cutoffDate = '2026-08-19'
const payload = {
  cutoff_date: cutoffDate,
  expenses: [{ date: '2026-08-03', category: 'Alimentación', amount: 40000 }],
}
const validPrediction = {
  cutoff_date: cutoffDate,
  projected_period: '2026-08',
  model_name: 'LinearRegression',
  prediction_objective: 'Estimación del gasto al cierre del mes en curso',
  categories: expenseCategories.map((category) => ({
    category, projected_amount: 10000, raw_prediction: 10000,
    nonnegative_adjustment: false,
  })),
  spent_to_date: 40000,
  total_projected_amount: 100000,
  previous_month_total: 0,
  has_previous_month_data: false,
  current_month_expenses_used: 1,
}

afterEach(() => { global.fetch = originalFetch })

test('envía cutoff_date y expenses y valida la respuesta definitiva', async () => {
  let sentBody
  global.fetch = async (_url, options) => {
    sentBody = JSON.parse(options.body)
    return { ok: true, status: 200, json: async () => validPrediction }
  }
  const result = await requestPrediction(payload)
  assert.deepEqual(sentBody, payload)
  assert.equal(result.projected_period, '2026-08')
  assert.equal(result.has_previous_month_data, false)
})

test('controla servicio FastAPI no disponible', async () => {
  global.fetch = async () => { throw new TypeError('fetch failed') }
  await assert.rejects(
    requestPrediction(payload),
    (error) => error instanceof AiServiceError
      && error.statusCode === 502
      && /no está disponible/i.test(error.message),
  )
})

test('rechaza una respuesta incompatible de FastAPI', async () => {
  global.fetch = async () => ({
    ok: true, status: 200, json: async () => ({ ...validPrediction, projected_period: '2026-09' }),
  })
  await assert.rejects(
    requestPrediction(payload),
    (error) => error instanceof AiServiceError && /respuesta inválida/i.test(error.message),
  )
})
