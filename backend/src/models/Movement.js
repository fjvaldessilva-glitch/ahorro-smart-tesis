const mongoose = require('mongoose')

const incomeCategories = ['Sueldo', 'Otros ingresos']
const expenseCategories = [
  'Alimentación',
  'Transporte',
  'Vivienda',
  'Servicios básicos',
  'Salud',
  'Educación',
  'Pago de deudas y créditos',
  'Entretenimiento',
  'Mascotas',
  'Otros gastos',
]

const movementSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true,
  },
  descripcion: {
    type: String,
    required: true,
    trim: true,
  },
  categoria: {
    type: String,
    required: true,
    enum: [...incomeCategories, ...expenseCategories],
  },
  tipo: {
    type: String,
    required: true,
    enum: ['Ingreso', 'Gasto'],
  },
  monto: {
    type: Number,
    required: true,
    min: 0.01,
  },
  fecha: {
    type: String,
    required: true,
    trim: true,
  },
}, {
  timestamps: true,
})

module.exports = mongoose.model('Movement', movementSchema)
