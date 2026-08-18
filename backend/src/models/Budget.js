const mongoose = require('mongoose')

const budgetSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  year: {
    type: Number,
    required: true,
    validate: {
      validator: Number.isInteger,
      message: 'El año del presupuesto debe ser un número entero.',
    },
  },
  month: {
    type: Number,
    required: true,
    min: 1,
    max: 12,
  },
  amount: {
    type: Number,
    required: true,
    validate: {
      validator: (amount) => Number.isFinite(amount) && amount > 0,
      message: 'El presupuesto debe ser un monto mayor que cero.',
    },
  },
}, {
  timestamps: true,
})

budgetSchema.index(
  { user: 1, year: 1, month: 1 },
  { unique: true },
)

module.exports = mongoose.model('Budget', budgetSchema)
