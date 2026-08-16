const mongoose = require('mongoose')

const connectDatabase = async () => {
  const mongodbUri = process.env.MONGODB_URI

  if (!mongodbUri) {
    throw new Error('La variable de entorno MONGODB_URI no está definida')
  }

  await mongoose.connect(mongodbUri)
  console.log(`MongoDB conectado: ${mongoose.connection.name}`)
}

module.exports = connectDatabase
