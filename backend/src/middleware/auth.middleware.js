const jwt = require('jsonwebtoken')

const authenticateToken = (request, response, next) => {
  const authorizationHeader = request.get('Authorization')
  const [scheme, token] = authorizationHeader?.split(' ') ?? []

  if (scheme !== 'Bearer' || !token) {
    return response.status(401).json({
      status: 'error',
      message: 'Token de autenticación requerido.',
    })
  }

  const jwtSecret = process.env.JWT_SECRET

  if (!jwtSecret) {
    console.error('La variable de entorno JWT_SECRET no está definida')
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible validar la autenticación.',
    })
  }

  try {
    const payload = jwt.verify(token, jwtSecret)

    if (!payload.sub) {
      return response.status(401).json({
        status: 'error',
        message: 'Token de autenticación inválido.',
      })
    }

    request.authenticatedUserId = payload.sub
    return next()
  } catch (_error) {
    return response.status(401).json({
      status: 'error',
      message: 'Token de autenticación inválido o expirado.',
    })
  }
}

module.exports = authenticateToken
