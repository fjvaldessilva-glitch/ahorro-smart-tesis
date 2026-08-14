const express = require('express')
const cors = require('cors')
const movementsRouter = require('./routes/movements.routes')

const app = express()
const PORT = 3001

app.use(cors({
  origin: 'http://localhost:5173',
}))

app.get('/api/health', (_request, response) => {
  response.json({
    status: 'ok',
    service: 'Ahorro Smart API',
  })
})

app.use('/api/movements', movementsRouter)

app.listen(PORT, () => {
  console.log(`Ahorro Smart API disponible en http://localhost:${PORT}`)
})
