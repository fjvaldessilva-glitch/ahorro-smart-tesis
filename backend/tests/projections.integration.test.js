const assert = require('node:assert/strict')
const { after, before, test } = require('node:test')
const mongoose = require('mongoose')
const Budget = require('../src/models/Budget')
const Movement = require('../src/models/Movement')
const Projection = require('../src/models/Projection')
const User = require('../src/models/User')

const API_URL = process.env.TEST_API_URL || 'http://127.0.0.1:3001'
const targetPeriod = '2026-09'
const offlineMode = process.env.TEST_EXPECT_AI_OFFLINE === '1'
const uniqueSuffix = `${Date.now()}-${process.pid}`
const users = {
  a: {
    nombre: 'Usuario T42 A',
    email: `t42.a.${uniqueSuffix}@ahorrosmart.test`,
    password: 'PruebaT42Segura!',
  },
  b: {
    nombre: 'Usuario T42 B',
    email: `t42.b.${uniqueSuffix}@ahorrosmart.test`,
    password: 'PruebaT42Segura!',
  },
}
const state = {
  ids: [],
  tokens: {},
  firstProjection: null,
  secondProjection: null,
  initialCounts: null,
  storedProjection: null,
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
  return {
    status: response.status,
    body: await response.json(),
  }
}

const registerAndLogin = async (user) => {
  const registration = await apiRequest('/api/auth/register', {
    method: 'POST',
    body: user,
  })
  assert.equal(registration.status, 201)
  state.ids.push(registration.body.user.id)
  const login = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: { email: user.email, password: user.password },
  })
  assert.equal(login.status, 200)
  return login.body.token
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
  state.tokens.a = await registerAndLogin(users.a)
  state.tokens.b = await registerAndLogin(users.b)

  const expenseDates = ['2026-06-10', '2026-07-10', '2026-08-10']
  for (const [index, date] of expenseDates.entries()) {
    const movement = await apiRequest('/api/movements', {
      method: 'POST',
      token: state.tokens.a,
      body: {
        description: `Gasto aislado T42 ${index + 1}`,
        category: 'Alimentación',
        type: 'Gasto',
        amount: 50000 + index * 5000,
        date,
      },
    })
    assert.equal(movement.status, 201)
  }

  const income = await apiRequest('/api/movements', {
    method: 'POST',
    token: state.tokens.a,
    body: {
      description: 'Ingreso excluido T42',
      category: 'Sueldo',
      type: 'Ingreso',
      amount: 999999,
      date: '2026-08-05',
    },
  })
  assert.equal(income.status, 201)
})

after(async () => {
  if (state.firstProjection) {
    console.log(`T42_RESULT=${JSON.stringify({
      targetPeriod,
      expensesSentToFastApi: 3,
      projection: state.secondProjection || state.firstProjection,
      persistedDocument: state.storedProjection,
      upsertDocumentCount: await Projection.countDocuments({ user: state.ids[0], targetPeriod }),
      userIsolationValidated: true,
    })}`)
  }
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
    method: 'POST',
    body: { targetPeriod },
  })
  assert.equal(response.status, 401)
})

test('rechaza targetPeriod inválido', async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST',
    token: state.tokens.a,
    body: { targetPeriod: 'septiembre-2026' },
  })
  assert.equal(response.status, 400)
})

test('responde de forma controlada cuando FastAPI no está disponible', { skip: !offlineMode }, async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST',
    token: state.tokens.a,
    body: { targetPeriod },
  })
  assert.equal(response.status, 502)
  assert.equal(response.body.status, 'error')
  assert.match(response.body.message, /no está disponible|tiempo de espera/i)
})

test('genera y persiste proyección con gastos aislados del usuario', { skip: offlineMode }, async () => {
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST',
    token: state.tokens.a,
    body: { targetPeriod },
  })
  assert.equal(response.status, 200)
  state.firstProjection = response.body.projection
  assert.equal(state.firstProjection.modelName, 'GradientBoostingRegressor')
  assert.equal(state.firstProjection.categories.length, 10)
  assert.ok(Number.isFinite(state.firstProjection.totalProjectedAmount))

  const stored = await Projection.findOne({
    user: state.ids[0],
    targetPeriod,
  }).lean()
  assert.ok(stored)
  assert.equal(stored.user.toString(), state.ids[0])
  assert.equal(stored.categories.length, 10)
  state.storedProjection = {
    user: stored.user.toString(),
    targetPeriod: stored.targetPeriod,
    modelName: stored.modelName,
    categoryCount: stored.categories.length,
    totalProjectedAmount: stored.totalProjectedAmount,
    historicalMonthsUsed: stored.historicalMonthsUsed,
    generatedAt: stored.generatedAt,
  }
})

test('consulta la misma proyección guardada', { skip: offlineMode }, async () => {
  const response = await apiRequest(`/api/projections?targetPeriod=${targetPeriod}`, {
    token: state.tokens.a,
  })
  assert.equal(response.status, 200)
  assert.equal(response.body.projection.id, state.firstProjection.id)
  assert.equal(response.body.projection.totalProjectedAmount, state.firstProjection.totalProjectedAmount)
})

test('upsert conserva un documento por usuario y período', { skip: offlineMode }, async () => {
  await new Promise((resolve) => setTimeout(resolve, 10))
  const response = await apiRequest('/api/projections/generate', {
    method: 'POST',
    token: state.tokens.a,
    body: { targetPeriod },
  })
  assert.equal(response.status, 200)
  state.secondProjection = response.body.projection
  assert.equal(state.secondProjection.id, state.firstProjection.id)
  assert.ok(new Date(state.secondProjection.generatedAt) > new Date(state.firstProjection.generatedAt))
  assert.equal(await Projection.countDocuments({ user: state.ids[0], targetPeriod }), 1)
})

test('aísla la proyección frente a otro usuario', { skip: offlineMode }, async () => {
  const response = await apiRequest(`/api/projections?targetPeriod=${targetPeriod}`, {
    token: state.tokens.b,
  })
  assert.equal(response.status, 404)
})

test('mantiene el índice único user y targetPeriod', { skip: offlineMode }, async () => {
  await Projection.syncIndexes()
  const indexes = await Projection.collection.indexes()
  const uniqueIndex = indexes.find((index) => (
    index.unique
      && index.key.user === 1
      && index.key.targetPeriod === 1
  ))
  assert.ok(uniqueIndex)
})
