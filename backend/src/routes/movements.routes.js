const express = require('express')

const router = express.Router()

router.get('/', (_request, response) => {
  response.json({
    status: 'ok',
    module: 'movements',
    message: 'Módulo de movimientos financieros preparado',
  })
})

module.exports = router
