const express = require('express')

const app = express()
const PORT = 3001

app.get('/api/health', (_request, response) => {
  response.json({
    status: 'ok',
    service: 'Ahorro Smart API',
  })
})

app.listen(PORT, () => {
  console.log(`Ahorro Smart API disponible en http://localhost:${PORT}`)
})
