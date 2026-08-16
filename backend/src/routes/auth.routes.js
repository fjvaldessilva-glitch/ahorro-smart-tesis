const express = require('express')
const bcrypt = require('bcryptjs')
const jwt = require('jsonwebtoken')
const User = require('../models/User')

const router = express.Router()
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const minimumPasswordLength = 8

router.use(express.json())

const getPublicUser = (user) => ({
  id: user._id,
  nombre: user.nombre,
  email: user.email,
})

router.post('/register', async (request, response) => {
  const nombre = String(request.body?.nombre ?? '').trim()
  const email = String(request.body?.email ?? '').trim().toLowerCase()
  const password = String(request.body?.password ?? '')

  if (!nombre || !email || !password) {
    return response.status(400).json({
      status: 'error',
      message: 'Nombre, correo electrónico y contraseña son obligatorios.',
    })
  }

  if (!emailPattern.test(email)) {
    return response.status(400).json({
      status: 'error',
      message: 'El formato del correo electrónico no es válido.',
    })
  }

  if (password.length < minimumPasswordLength) {
    return response.status(400).json({
      status: 'error',
      message: 'La contraseña debe tener al menos 8 caracteres.',
    })
  }

  try {
    const existingUser = await User.findOne({ email })

    if (existingUser) {
      return response.status(409).json({
        status: 'error',
        message: 'El correo electrónico ya está registrado.',
      })
    }

    const passwordHash = await bcrypt.hash(password, 12)
    const user = await User.create({ nombre, email, passwordHash })

    return response.status(201).json({
      status: 'ok',
      user: getPublicUser(user),
    })
  } catch (error) {
    if (error?.code === 11000) {
      return response.status(409).json({
        status: 'error',
        message: 'El correo electrónico ya está registrado.',
      })
    }

    console.error(`Error al registrar usuario: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible registrar el usuario.',
    })
  }
})

router.post('/login', async (request, response) => {
  const email = String(request.body?.email ?? '').trim().toLowerCase()
  const password = String(request.body?.password ?? '')

  if (!email || !password) {
    return response.status(400).json({
      status: 'error',
      message: 'Correo electrónico y contraseña son obligatorios.',
    })
  }

  try {
    const user = await User.findOne({ email }).select('+passwordHash')
    const validPassword = user
      ? await bcrypt.compare(password, user.passwordHash)
      : false

    if (!user || !validPassword) {
      return response.status(401).json({
        status: 'error',
        message: 'Credenciales incorrectas.',
      })
    }

    const jwtSecret = process.env.JWT_SECRET

    if (!jwtSecret) {
      throw new Error('La variable de entorno JWT_SECRET no está definida')
    }

    const token = jwt.sign(
      { sub: user._id.toString() },
      jwtSecret,
      { expiresIn: '1h' },
    )

    return response.json({
      status: 'ok',
      token,
      user: getPublicUser(user),
    })
  } catch (error) {
    console.error(`Error al iniciar sesión: ${error.message}`)
    return response.status(500).json({
      status: 'error',
      message: 'No fue posible iniciar sesión.',
    })
  }
})

module.exports = router
