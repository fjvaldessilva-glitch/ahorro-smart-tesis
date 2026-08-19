const express = require('express')
const cors = require('cors')
const connectDatabase = require('./config/database')
const authRouter = require('./routes/auth.routes')
const budgetRouter = require('./routes/budget.routes')
const movementsRouter = require('./routes/movements.routes')
const projectionsRouter = require('./routes/projections.routes')

const app = express()
const PORT = Number(process.env.PORT) || 3001

app.use(cors({
  origin: 'http://localhost:5173',
}))

app.get('/api/health', (_request, response) => {
  response.json({
    status: 'ok',
    service: 'Ahorro Smart API',
  })
})

app.use('/api/auth', authRouter)
app.use('/api/budget', budgetRouter)
app.use('/api/movements', movementsRouter)
app.use('/api/projections', projectionsRouter)

const startServer = async () => {
  try {
    await connectDatabase()

    app.listen(PORT, () => {
      console.log(`Ahorro Smart API disponible en http://localhost:${PORT}`)
    })
  } catch (error) {
    console.error(`No fue posible iniciar Ahorro Smart API: ${error.message}`)
    process.exitCode = 1
  }
}

startServer()
