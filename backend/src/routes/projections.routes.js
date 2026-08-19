const express = require('express')
const authenticateToken = require('../middleware/auth.middleware')
const {
  generateProjection,
  getProjection,
} = require('../controllers/projections.controller')

const router = express.Router()

router.use(express.json())
router.use(authenticateToken)

router.post('/generate', generateProjection)
router.get('/', getProjection)

module.exports = router
