const mongoose = require('mongoose')
const { expenseCategories } = require('../constants/movement-categories')

const categoryProjectionSchema = new mongoose.Schema({
  category: {
    type: String,
    required: true,
    enum: expenseCategories,
  },
  projectedAmount: {
    type: Number,
    required: true,
    min: 0,
    validate: Number.isFinite,
  },
  rawPrediction: {
    type: Number,
    required: true,
    validate: Number.isFinite,
  },
  nonnegativeAdjustment: {
    type: Boolean,
    required: true,
  },
}, {
  _id: false,
})

const projectionSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  targetPeriod: {
    type: String,
    required: true,
    match: /^\d{4}-(0[1-9]|1[0-2])$/,
  },
  modelName: {
    type: String,
    required: true,
    trim: true,
  },
  categories: {
    type: [categoryProjectionSchema],
    required: true,
    validate: {
      validator(categories) {
        const receivedCategories = categories.map(({ category }) => category)
        return categories.length === expenseCategories.length
          && new Set(receivedCategories).size === expenseCategories.length
          && expenseCategories.every((category) => receivedCategories.includes(category))
      },
      message: 'La proyección debe contener exactamente las diez categorías oficiales de gasto.',
    },
  },
  totalProjectedAmount: {
    type: Number,
    required: true,
    min: 0,
    validate: Number.isFinite,
  },
  historicalMonthsUsed: {
    type: Number,
    required: true,
    min: 3,
    validate: Number.isInteger,
  },
  generatedAt: {
    type: Date,
    required: true,
  },
}, {
  timestamps: true,
})

projectionSchema.index(
  { user: 1, targetPeriod: 1 },
  { unique: true },
)

module.exports = mongoose.model('Projection', projectionSchema)
