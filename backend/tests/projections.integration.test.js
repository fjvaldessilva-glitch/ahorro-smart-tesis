const assert = require('node:assert/strict')
const { after, before, test } = require('node:test')
const mongoose = require('mongoose')
const Budget = require('../src/models/Budget')
const Movement = require('../src/models/Movement')
const Projection = require('../src/models/Projection')
const User = require('../src/models/User')

const API_URL = process.env.TEST_API_URL || 'http://127.0.0.1:3001'
const cutoffDate = '2026-08-19'
const projectedPeriod = '2026-08'
const uniqueSuffix = `${Date.now()}-${process.pid}`
const users = Object.fromEntries(['a', 'b', 'c'].map((key) => [key, {
  nombre: `Usuario T42 ${key.toUpperCase()}`,
  email: `t42.${key}.${uniqueSuffix}@ahorrosmart.test`,
  password: 'PruebaT42Segura!',
}]))
const state = {
  ids: [],
  tokens: {},
  firstProjection: null,
  initialCounts: null,
}

const apiRequest = async (path, { method = 'GET', token, body } = {}) => {
  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  })
  return { status: response.status, body: await response.json() }
}

const registerAndLogin = async (user) => {
  const registration = await apiRequest('/api/auth/register', { method: 'POST', body: user })
  assert.equal(registration.status, 201)
  state.ids.push(registration.body.user.id)
  const login = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: { email: user.email, password: user.password },
  })
  assert.equal(login.status, 200)
  return login.body.token
}

const createMovement = async (token, body) => {
  const response = await apiRequest('/api/movements', { method: 'POST', token, body })
  assert.equal(response.status, 201)
}

before(async () => {
  assert.ok(process.env.MONGODB_URI, 'MONGODB_URI es obligatoria para la prueba integral.')
  await mongoose.connect(process.env.MONGODB_URI)
  state.initialCounts = {
    users: await User.countDocuments(),
    movements: await Movement.countDocuments(),
    budgets: await Budget.countDocuments(),
    projections: await Projection.countDocuments(),
  }
  for (const key of Object.keys(users)) state.tokens[key] = await registerAndLogin(users[key])

  await createMovement(state.tokens.a, {
    description: 'Gasto actual aislado T42', category: 'Alimentación', type: 'Gasto',
    amount: 40000, date: '2026-08-03',
  })
  await createMovement(state.tokens.a, {
    description: 'Ingreso excluido T42', category: 'Sueldo', type: 'Ingreso',
    amount: 999999, date: '2026-08-05',
  })
  await createMovement(state.tokens.a, {
    description: 'Gasto posterior excluido T42', category: 'Salud', type: 'Gasto',
    amount: 70000, date: '2026-08-25',
  })
  await createMovement(state.tokens.b, {
    description: 'Solo historial previo T42', category: 'Vivienda', type: 'Gasto',
    amount: 90000, date: '2026-07-10',
  })
  await createMovement(state.tokens.c, {
    description: 'Historial previo T42', category: 'Vivienda', type: 'Gasto',
    amount: 50000, date: '2026-07-10',
  })
  await createMovement(state.tokens.c, {
    description: 'Gasto actual con historial T42', category: 'Transporte', type: 'Gasto',
    amount: 20000, date: '2026-08-10',
  })
})

after(async () => {
  if (state.ids.length > 0) {
    await Promise.all([
      Projection.deleteMany({ user: { $in: state.ids } }),
      Movement.deleteMany({ user: { $in: state.ids } }),
      Budget.deleteMany({ user: { $in: state.ids } }),
      User.deleteMany({ _id: { $in: state.ids } }),
    ])
  }
  assert.deepEqual({
    users: await User.countDocuments(),
    movements: await Movement.countDocuments(),
    budgets: await Budget.countDocuments(),
    projections: await Projection.countDocuments(),
  }, state.initialCounts)
  await mongoose.disconnect()
})

test('rechaza generación sin autenticación', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST', body: { cutoffDate },
  })
  assert.equal(response.status, 401)
})

test('rechaza cutoffDate inválida', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST', token: state.tokens.a, body: { cutoffDate: '2026-02-30' },
  })
  assert.equal(response.status, 400)
})

test('rechaza usuario sin gastos del mes en curso', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST', token: state.tokens.b, body: { cutoffDate },
  })
  assert.equal(response.status, 422)
  assert.match(response.body.message, /No existen gastos registrados en el mes en curso/i)
})

test('genera sin historial previo y excluye ingresos y gastos posteriores', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST', token: state.tokens.a, body: { cutoffDate },
  })
  assert.equal(response.status, 200)
  state.firstProjection = response.body.projection
  assert.equal(state.firstProjection.projectedPeriod, projectedPeriod)
  assert.equal(state.firstProjection.modelName, 'LinearRegression')
  assert.equal(state.firstProjection.spentToDate, 40000)
  assert.equal(state.firstProjection.currentMonthExpensesUsed, 1)
  assert.equal(state.firstProjection.previousMonthTotal, 0)
  assert.equal(state.firstProjection.hasPreviousMonthData, false)
  assert.equal(state.firstProjection.categories.length, 10)
  assert.equal('targetPeriod' in state.firstProjection, false)
})

test('genera con historial del mes anterior opcional', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST', token: state.tokens.c, body: { cutoffDate },
  })
  assert.equal(response.status, 200)
  assert.equal(response.body.projection.spentToDate, 20000)
  assert.equal(response.body.projection.previousMonthTotal, 50000)
  assert.equal(response.body.projection.hasPreviousMonthData, true)
})

test('persiste campos definitivos y targetPeriod interno', async () => {
  const stored = await Projection.findOne({ user: state.ids[0], targetPeriod: projectedPeriod }).lean()
  assert.ok(stored)
  assert.equal(stored.cutoffDate, cutoffDate)
  assert.equal(stored.modelName, 'LinearRegression')
  assert.equal(stored.spentToDate, 40000)
  assert.equal(stored.currentMonthExpensesUsed, 1)
})

test('consulta por projectedPeriod la misma proyección', async () => {
  const response = await apiRequest(`/api/projections?projectedPeriod=${projectedPeriod}`, {
    token: state.tokens.a,
  })
  assert.equal(response.status, 200)
  assert.equal(response.body.projection.id, state.firstProjection.id)
  assert.equal(response.body.projection.projectedPeriod, projectedPeriod)
})

test('upsert conserva un documento por usuario y período', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST', token: state.tokens.a, body: { cutoffDate },
  })
  assert.equal(response.status, 200)
  assert.equal(response.body.projection.id, state.firstProjection.id)
  assert.equal(await Projection.countDocuments({ user: state.ids[0], targetPeriod: projectedPeriod }), 1)
})

test('aísla la proyección frente a otro usuario', async () => {
  const response = await apiRequest(`/api/projections?projectedPeriod=${projectedPeriod}`, {
    token: state.tokens.b,
  })
  assert.equal(response.status, 404)
})

test('mantiene el índice único user y targetPeriod', async () => {
  await Projection.syncIndexes()
  const indexes = await Projection.collection.indexes()
  assert.ok(indexes.some((index) => (
    index.unique && index.key.user === 1 && index.key.targetPeriod === 1
  )))
})
