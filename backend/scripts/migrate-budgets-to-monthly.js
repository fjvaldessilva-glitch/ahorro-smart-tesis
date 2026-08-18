const mongoose = require('mongoose')

const migrateBudgetsToMonthly = async () => {
  const mongodbUri = process.env.MONGODB_URI

  if (!mongodbUri) {
    throw new Error('La variable de entorno MONGODB_URI no está definida.')
  }

  await mongoose.connect(mongodbUri)

  const budgets = mongoose.connection.collection('budgets')
  const existingBudgets = await budgets.find({}).toArray()
  const legacyBudgets = existingBudgets.filter(
    (budget) => !Number.isInteger(budget.year) || !Number.isInteger(budget.month),
  )

  const destinationKeys = new Map()

  for (const budget of existingBudgets) {
    const createdAt = new Date(budget.createdAt)
    const year = Number.isInteger(budget.year)
      ? budget.year
      : createdAt.getUTCFullYear()
    const month = Number.isInteger(budget.month)
      ? budget.month
      : createdAt.getUTCMonth() + 1

    if (!Number.isInteger(year) || !Number.isInteger(month) || month < 1 || month > 12) {
      throw new Error(`No fue posible determinar el período de ${budget._id}.`)
    }

    const destinationKey = `${budget.user}:${year}:${month}`

    if (destinationKeys.has(destinationKey)) {
      throw new Error(
        `Conflicto de unicidad entre ${destinationKeys.get(destinationKey)} y ${budget._id}.`,
      )
    }

    destinationKeys.set(destinationKey, budget._id.toString())
  }

  if (legacyBudgets.length > 0) {
    await budgets.bulkWrite(legacyBudgets.map((budget) => {
      const createdAt = new Date(budget.createdAt)

      return {
        updateOne: {
          filter: { _id: budget._id },
          update: {
            $set: {
              year: createdAt.getUTCFullYear(),
              month: createdAt.getUTCMonth() + 1,
            },
          },
        },
      }
    }))
  }

  const indexes = await budgets.indexes()

  if (indexes.some((index) => index.name === 'user_1' && index.unique)) {
    await budgets.dropIndex('user_1')
  }

  await budgets.createIndex(
    { user: 1, year: 1, month: 1 },
    { unique: true, name: 'user_1_year_1_month_1' },
  )

  const finalCount = await budgets.countDocuments()

  console.log(`Presupuestos antes de migrar: ${existingBudgets.length}`)
  console.log(`Presupuestos legacy migrados: ${legacyBudgets.length}`)
  console.log(`Presupuestos después de migrar: ${finalCount}`)
  console.log('Presupuestos eliminados: 0')
}

migrateBudgetsToMonthly()
  .catch((error) => {
    console.error(`Migración detenida: ${error.message}`)
    process.exitCode = 1
  })
  .finally(async () => {
    await mongoose.disconnect()
  })
