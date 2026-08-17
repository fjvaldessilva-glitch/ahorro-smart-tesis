const mongoose = require('mongoose')
const {
  categoriesByType,
  movementCategories,
  movementTypes,
} = require('../constants/movement-categories')

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
    enum: movementCategories,
    validate: {
      validator(category) {
        const update = typeof this.getUpdate === 'function'
          ? this.getUpdate()?.$set
          : null
        const movementType = this.tipo ?? update?.tipo

        return categoriesByType[movementType]?.includes(category) ?? false
      },
      message: 'La categoría no corresponde al tipo de movimiento.',
    },
  },
  tipo: {
    type: String,
    required: true,
    enum: movementTypes,
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
