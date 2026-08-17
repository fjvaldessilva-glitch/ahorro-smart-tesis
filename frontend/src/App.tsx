import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import ahorroSmartLogo from './assets/ahorro-smart-logo.png'
import './App.css'

type Tab = 'movements' | 'analysis' | 'projection'
type MovementType = 'Ingreso' | 'Gasto'
type DateFilter = 'all' | 'day' | 'week' | 'month' | 'range'
type AuthMode = 'login' | 'register'

type Movement = {
  id: string
  description: string
  category: string
  type: MovementType
  amount: number
  date: string
}

type AuthUser = {
  id: string
  nombre: string
  email: string
}

type AuthSession = {
  token: string
  user: AuthUser
}

type ApiMessage = {
  message?: string
}

type BudgetResponse = {
  budget: {
    id: string
    amount: number
  } | null
}

const incomeCategories = [
  'Sueldo',
  'Otros ingresos',
]

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

const categoriesByType: Record<MovementType, string[]> = {
  Ingreso: incomeCategories,
  Gasto: expenseCategories,
}

const currencyFormatter = new Intl.NumberFormat('es-CL', {
  style: 'currency',
  currency: 'CLP',
  maximumFractionDigits: 0,
})

const compactCurrencyFormatter = new Intl.NumberFormat('es-CL', {
  style: 'currency',
  currency: 'CLP',
  notation: 'compact',
  maximumFractionDigits: 1,
})

const movementsApiUrl = 'http://localhost:3001/api/movements'
const budgetApiUrl = 'http://localhost:3001/api/budget'
const authApiUrl = 'http://localhost:3001/api/auth'
const authStorageKey = 'ahorroSmart.authSession'
const categoryColors = ['#23cfa6', '#20bce8', '#67d94b', '#ffb547', '#ff7187', '#8b7cf6']
const descriptionLetterPattern = /\p{L}/u

const getStoredAuthSession = (): AuthSession | null => {
  try {
    const storedSession = localStorage.getItem(authStorageKey)

    if (!storedSession) return null

    const parsedSession = JSON.parse(storedSession) as Partial<AuthSession>
    const user = parsedSession.user

    if (
      typeof parsedSession.token !== 'string'
      || !user
      || typeof user.id !== 'string'
      || typeof user.nombre !== 'string'
      || typeof user.email !== 'string'
    ) {
      localStorage.removeItem(authStorageKey)
      return null
    }

    return parsedSession as AuthSession
  } catch {
    localStorage.removeItem(authStorageKey)
    return null
  }
}

const getApiMessage = async (response: Response, fallback: string) => {
  try {
    const data = await response.json() as ApiMessage
    return data.message || fallback
  } catch {
    return fallback
  }
}

const getWeekRange = (referenceDate: string) => {
  const [year, month, day] = referenceDate.split('-').map(Number)
  const date = new Date(Date.UTC(year, month - 1, day))
  const daysSinceMonday = (date.getUTCDay() + 6) % 7
  const startDate = new Date(date)
  const endDate = new Date(date)

  startDate.setUTCDate(date.getUTCDate() - daysSinceMonday)
  endDate.setUTCDate(startDate.getUTCDate() + 6)

  return {
    start: startDate.toISOString().slice(0, 10),
    end: endDate.toISOString().slice(0, 10),
  }
}

const formatMovementDate = (movementDate: string) => {
  const [year, month, day] = movementDate.split('-')
  return `${day}-${month}-${year}`
}

const getCurrentMonth = () => {
  const currentDate = new Date()
  const year = currentDate.getFullYear()
  const month = String(currentDate.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

function App() {
  const [authSession, setAuthSession] = useState<AuthSession | null>(getStoredAuthSession)
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [authName, setAuthName] = useState('')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authError, setAuthError] = useState('')
  const [authSuccess, setAuthSuccess] = useState('')
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('movements')
  const [movements, setMovements] = useState<Movement[]>([])
  const [budget, setBudget] = useState<number | null>(null)
  const [budgetInput, setBudgetInput] = useState('')
  const [budgetError, setBudgetError] = useState('')
  const [budgetSuccess, setBudgetSuccess] = useState('')
  const [isBudgetSaving, setIsBudgetSaving] = useState(false)
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState(incomeCategories[0])
  const [type, setType] = useState<MovementType>('Ingreso')
  const [amount, setAmount] = useState('')
  const [date, setDate] = useState('')
  const [communicationError, setCommunicationError] = useState('')
  const [descriptionError, setDescriptionError] = useState('')
  const [dateFilter, setDateFilter] = useState<DateFilter>('month')
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedMonth, setSelectedMonth] = useState(getCurrentMonth)
  const [rangeStart, setRangeStart] = useState('')
  const [rangeEnd, setRangeEnd] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [movementsPerPage, setMovementsPerPage] = useState(10)

  const clearAuthSession = (message = '') => {
    localStorage.removeItem(authStorageKey)
    setAuthSession(null)
    setMovements([])
    setBudget(null)
    setBudgetInput('')
    setBudgetError('')
    setBudgetSuccess('')
    setCommunicationError('')
    setAuthPassword('')
    setAuthError(message)
  }

  useEffect(() => {
    if (!authSession) return

    const loadMovements = async () => {
      try {
        const response = await fetch(movementsApiUrl, {
          headers: {
            Authorization: `Bearer ${authSession.token}`,
          },
        })

        if (response.status === 401) {
          clearAuthSession('Tu sesión expiró o no es válida. Inicia sesión nuevamente.')
          return
        }

        if (!response.ok) {
          throw new Error(await getApiMessage(
            response,
            'No fue posible consultar los movimientos.',
          ))
        }

        const apiMovements = await response.json() as Movement[]
        setMovements(apiMovements)
        setCommunicationError('')
      } catch (error) {
        console.error(error)
        setCommunicationError('No fue posible conectar con el backend.')
      }
    }

    void loadMovements()
  }, [authSession])

  useEffect(() => {
    if (!authSession) return

    const loadBudget = async () => {
      try {
        const response = await fetch(budgetApiUrl, {
          headers: {
            Authorization: `Bearer ${authSession.token}`,
          },
        })

        if (response.status === 401) {
          clearAuthSession('Tu sesión expiró o no es válida. Inicia sesión nuevamente.')
          return
        }

        if (!response.ok) {
          throw new Error(await getApiMessage(
            response,
            'No fue posible consultar el presupuesto.',
          ))
        }

        const data = await response.json() as BudgetResponse
        const currentBudget = data.budget?.amount ?? null

        setBudget(currentBudget)
        setBudgetInput(currentBudget ? String(currentBudget) : '')
        setBudgetError('')
      } catch (error) {
        console.error(error)
        setBudgetError('No fue posible consultar el presupuesto.')
      }
    }

    void loadBudget()
  }, [authSession])

  const filteredMovements = useMemo(() => {
    if (dateFilter === 'all') return movements

    if (dateFilter === 'day') {
      return selectedDate
        ? movements.filter((movement) => movement.date === selectedDate)
        : []
    }

    if (dateFilter === 'week') {
      if (!selectedDate) return []

      const weekRange = getWeekRange(selectedDate)
      return movements.filter(
        (movement) => movement.date >= weekRange.start
          && movement.date <= weekRange.end,
      )
    }

    if (dateFilter === 'month') {
      return selectedMonth
        ? movements.filter((movement) => movement.date.startsWith(selectedMonth))
        : []
    }

    if (!rangeStart || !rangeEnd || rangeStart > rangeEnd) return []

    return movements.filter(
      (movement) => movement.date >= rangeStart && movement.date <= rangeEnd,
    )
  }, [dateFilter, movements, rangeEnd, rangeStart, selectedDate, selectedMonth])

  const totalPages = Math.max(
    1,
    Math.ceil(filteredMovements.length / movementsPerPage),
  )
  const safeCurrentPage = Math.min(currentPage, totalPages)
  const paginatedMovements = useMemo(() => {
    const firstMovementIndex = (safeCurrentPage - 1) * movementsPerPage
    return filteredMovements.slice(
      firstMovementIndex,
      firstMovementIndex + movementsPerPage,
    )
  }, [filteredMovements, movementsPerPage, safeCurrentPage])

  useEffect(() => {
    setCurrentPage(1)
  }, [dateFilter, rangeEnd, rangeStart, selectedDate, selectedMonth])

  useEffect(() => {
    setCurrentPage((page) => Math.min(page, totalPages))
  }, [totalPages])

  const summary = useMemo(() => {
    const totalIncome = filteredMovements
      .filter((movement) => movement.type === 'Ingreso')
      .reduce((total, movement) => total + movement.amount, 0)
    const totalExpenses = filteredMovements
      .filter((movement) => movement.type === 'Gasto')
      .reduce((total, movement) => total + movement.amount, 0)

    return {
      totalIncome,
      totalExpenses,
      balance: totalIncome - totalExpenses,
      budgetUsed: totalIncome > 0 ? (totalExpenses / totalIncome) * 100 : 0,
    }
  }, [filteredMovements])

  const budgetExecution = budget && budget > 0
    ? (summary.totalExpenses / budget) * 100
    : null

  const expensesByCategory = useMemo(() => {
    const totals = filteredMovements
      .filter((movement) => movement.type === 'Gasto')
      .reduce<Record<string, number>>((result, movement) => {
        result[movement.category] = (result[movement.category] ?? 0) + movement.amount
        return result
      }, {})

    return Object.entries(totals)
      .map(([name, total]) => ({
        name,
        total,
        percentage: summary.totalExpenses > 0
          ? (total / summary.totalExpenses) * 100
          : 0,
      }))
      .sort((first, second) => second.total - first.total)
  }, [filteredMovements, summary.totalExpenses])

  const expensesByDate = useMemo(() => {
    const totalsByDate = filteredMovements
      .filter((movement) => movement.type === 'Gasto')
      .reduce<Record<string, { date: string; total: number }>>((result, movement) => {
      const dateTotals = result[movement.date] ?? {
        date: movement.date,
        total: 0,
      }

      dateTotals.total += movement.amount
      result[movement.date] = dateTotals
      return result
    }, {})

    return Object.values(totalsByDate).sort(
      (first, second) => first.date.localeCompare(second.date),
    )
  }, [filteredMovements])

  const comparisonMaximum = Math.max(summary.totalIncome, summary.totalExpenses)
  const incomeBarHeight = comparisonMaximum > 0
    ? (summary.totalIncome / comparisonMaximum) * 100
    : 0
  const expenseBarHeight = comparisonMaximum > 0
    ? (summary.totalExpenses / comparisonMaximum) * 100
    : 0

  const expenseDonutGradient = useMemo(() => {
    let accumulatedPercentage = 0
    const segments = expensesByCategory.map((categoryItem, index) => {
      const start = accumulatedPercentage
      accumulatedPercentage += categoryItem.percentage
      return `${categoryColors[index % categoryColors.length]} ${start}% ${accumulatedPercentage}%`
    })

    return `conic-gradient(${segments.join(', ')})`
  }, [expensesByCategory])

  const trendDataMaximum = Math.max(
    ...expensesByDate.map((item) => item.total),
    0,
  )
  const trendMaximum = trendDataMaximum > 0 ? trendDataMaximum : 1
  const trendChartWidth = Math.max(720, 139 + expensesByDate.length * 90)
  const trendChartHeight = 250
  const trendChartLeftPadding = 105
  const trendChartRightPadding = 34
  const trendChartTopPadding = 28
  const trendChartBottomPadding = 48
  const trendScalePositions = [0, 0.25, 0.5, 0.75, 1]
  const trendAvailableWidth = trendChartWidth - trendChartLeftPadding - trendChartRightPadding
  const trendAvailableHeight = trendChartHeight - trendChartTopPadding - trendChartBottomPadding
  const trendGroupWidth = trendAvailableWidth / Math.max(expensesByDate.length, 1)
  const trendBarWidth = Math.min(42, trendGroupWidth * 0.48)

  const availableCategories = categoriesByType[type]

  const handleTypeChange = (newType: MovementType) => {
    setType(newType)
    setCategory(categoriesByType[newType][0])
  }

  const handleBudgetSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const numericBudget = Number(budgetInput)

    if (!budgetInput.trim() || !Number.isFinite(numericBudget) || numericBudget <= 0) {
      setBudgetError('Ingresa un presupuesto mayor que cero.')
      setBudgetSuccess('')
      return
    }

    setIsBudgetSaving(true)
    setBudgetError('')
    setBudgetSuccess('')

    try {
      const response = await fetch(budgetApiUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authSession?.token ?? ''}`,
        },
        body: JSON.stringify({ amount: numericBudget }),
      })

      if (response.status === 401) {
        clearAuthSession('Tu sesión expiró o no es válida. Inicia sesión nuevamente.')
        return
      }

      if (!response.ok) {
        setBudgetError(await getApiMessage(
          response,
          'No fue posible guardar el presupuesto.',
        ))
        return
      }

      const data = await response.json() as BudgetResponse
      const savedBudget = data.budget?.amount ?? null

      setBudget(savedBudget)
      setBudgetInput(savedBudget ? String(savedBudget) : '')
      setBudgetSuccess('Presupuesto guardado correctamente.')
    } catch (error) {
      console.error(error)
      setBudgetError('No fue posible conectar con el backend.')
    } finally {
      setIsBudgetSaving(false)
    }
  }

  const handleAuthSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setAuthError('')
    setAuthSuccess('')
    setIsAuthSubmitting(true)

    try {
      if (authMode === 'register') {
        const response = await fetch(`${authApiUrl}/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            nombre: authName.trim(),
            email: authEmail.trim(),
            password: authPassword,
          }),
        })

        if (!response.ok) {
          setAuthError(await getApiMessage(response, 'No fue posible crear la cuenta.'))
          return
        }

        setAuthMode('login')
        setAuthName('')
        setAuthPassword('')
        setAuthSuccess('Cuenta creada correctamente. Ya puedes iniciar sesión.')
        return
      }

      const response = await fetch(`${authApiUrl}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: authEmail.trim(),
          password: authPassword,
        }),
      })

      if (!response.ok) {
        setAuthError(await getApiMessage(response, 'No fue posible iniciar sesión.'))
        return
      }

      const session = await response.json() as AuthSession & { status: string }
      const nextSession = {
        token: session.token,
        user: session.user,
      }

      localStorage.setItem(authStorageKey, JSON.stringify(nextSession))
      setAuthSession(nextSession)
      setAuthPassword('')
      setAuthError('')
      setAuthSuccess('')
      setActiveTab('movements')
    } catch (error) {
      console.error(error)
      setAuthError('No fue posible conectar con el backend.')
    } finally {
      setIsAuthSubmitting(false)
    }
  }

  const handleLogout = () => {
    clearAuthSession()
    setAuthEmail('')
    setAuthSuccess('')
    setActiveTab('movements')
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const movementDescription = String(formData.get('description') ?? '').trim()
    const movementCategory = String(formData.get('category') ?? '')
    const movementType = String(formData.get('type') ?? '') as MovementType
    const numericAmount = Number(formData.get('amount'))
    const movementDate = String(formData.get('date') ?? '')

    const isKnownType = movementType === 'Ingreso' || movementType === 'Gasto'
    const isCompatibleCategory = isKnownType
      && categoriesByType[movementType].includes(movementCategory)

    if (!descriptionLetterPattern.test(movementDescription)) {
      setDescriptionError('La descripción debe contener al menos una letra.')
      return
    }

    setDescriptionError('')

    if (
      !movementDate
      || numericAmount <= 0
      || !isCompatibleCategory
    ) return

    try {
      const response = await fetch(movementsApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authSession?.token ?? ''}`,
        },
        body: JSON.stringify({
          description: movementDescription,
          category: movementCategory,
          type: movementType,
          amount: numericAmount,
          date: movementDate,
        }),
      })

      if (response.status === 401) {
        clearAuthSession('Tu sesión expiró o no es válida. Inicia sesión nuevamente.')
        return
      }

      if (!response.ok) {
        throw new Error(await getApiMessage(
          response,
          'No fue posible registrar el movimiento.',
        ))
      }

      const createdMovement = await response.json() as Movement
      setMovements((currentMovements) => [
        ...currentMovements,
        createdMovement,
      ])
      setCommunicationError('')
      setDescription('')
      setAmount('')
      setDate('')
    } catch (error) {
      console.error(error)
      setCommunicationError('No fue posible registrar el movimiento en el backend.')
    }
  }

  const removeMovement = async (id: string) => {
    try {
      const response = await fetch(`${movementsApiUrl}/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authSession?.token ?? ''}`,
        },
      })

      if (response.status === 401) {
        clearAuthSession('Tu sesión expiró o no es válida. Inicia sesión nuevamente.')
        return
      }

      if (!response.ok) {
        throw new Error(await getApiMessage(
          response,
          'No fue posible eliminar el movimiento.',
        ))
      }

      setMovements((currentMovements) =>
        currentMovements.filter((movement) => movement.id !== id),
      )
      setCommunicationError('')
    } catch (error) {
      console.error(error)
      setCommunicationError('No fue posible eliminar el movimiento en el backend.')
    }
  }

  if (!authSession) {
    return (
      <div className="app-shell auth-shell">
        <header className="app-header">
          <div className="app-header__content">
            <img
              className="app-header__logo"
              src={ahorroSmartLogo}
              alt="Logo de Ahorro Smart"
            />
            <p>Controla tus gastos y organiza tu presupuesto.</p>
          </div>
        </header>

        <main className="auth-workspace">
          <section className="auth-card" aria-labelledby="auth-title">
            <div className="auth-card__heading">
              <p>Acceso seguro</p>
              <h1 id="auth-title">
                {authMode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}
              </h1>
              <span>
                {authMode === 'login'
                  ? 'Ingresa para consultar tus movimientos financieros.'
                  : 'Crea una cuenta para comenzar a organizar tus finanzas.'}
              </span>
            </div>

            <div className="auth-mode" aria-label="Opciones de autenticación">
              <button
                className={authMode === 'login'
                  ? 'auth-mode__button auth-mode__button--active'
                  : 'auth-mode__button'}
                type="button"
                onClick={() => {
                  setAuthMode('login')
                  setAuthError('')
                  setAuthSuccess('')
                  setAuthPassword('')
                }}
              >
                Iniciar sesión
              </button>
              <button
                className={authMode === 'register'
                  ? 'auth-mode__button auth-mode__button--active'
                  : 'auth-mode__button'}
                type="button"
                onClick={() => {
                  setAuthMode('register')
                  setAuthError('')
                  setAuthSuccess('')
                  setAuthPassword('')
                }}
              >
                Crear cuenta
              </button>
            </div>

            {authError && (
              <div className="auth-message auth-message--error" role="alert">
                {authError}
              </div>
            )}

            {authSuccess && (
              <div className="auth-message auth-message--success" role="status">
                {authSuccess}
              </div>
            )}

            <form className="auth-form" onSubmit={handleAuthSubmit}>
              {authMode === 'register' && (
                <label className="field">
                  <span>Nombre</span>
                  <input
                    type="text"
                    value={authName}
                    onChange={(event) => setAuthName(event.target.value)}
                    autoComplete="name"
                    required
                  />
                </label>
              )}

              <label className="field">
                <span>Correo electrónico</span>
                <input
                  type="email"
                  value={authEmail}
                  onChange={(event) => setAuthEmail(event.target.value)}
                  autoComplete="email"
                  required
                />
              </label>

              <label className="field">
                <span>Contraseña</span>
                <input
                  type="password"
                  value={authPassword}
                  onChange={(event) => setAuthPassword(event.target.value)}
                  autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                  minLength={8}
                  required
                />
              </label>

              <button className="primary-button auth-submit" type="submit" disabled={isAuthSubmitting}>
                {isAuthSubmitting
                  ? 'Procesando...'
                  : authMode === 'login' ? 'Ingresar' : 'Crear cuenta'}
              </button>
            </form>
          </section>
        </main>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__content">
          <img
            className="app-header__logo"
            src={ahorroSmartLogo}
            alt="Logo de Ahorro Smart"
          />
          <p>Controla tus gastos y organiza tu presupuesto.</p>
          <div className="session-summary">
            <span>
              Sesión de <strong>{authSession.user.nombre}</strong>
              {' · '}{authSession.user.email}
            </span>
            <button type="button" onClick={handleLogout}>Cerrar sesión</button>
          </div>
        </div>
      </header>

      <nav className="main-nav" aria-label="Módulos principales">
        <div className="main-nav__content" role="tablist">
          <button
            className={activeTab === 'movements' ? 'tab tab--active' : 'tab'}
            type="button"
            role="tab"
            aria-selected={activeTab === 'movements'}
            onClick={() => setActiveTab('movements')}
          >
            Ingresos/Gastos
          </button>
          <button
            className={activeTab === 'analysis' ? 'tab tab--active' : 'tab'}
            type="button"
            role="tab"
            aria-selected={activeTab === 'analysis'}
            onClick={() => setActiveTab('analysis')}
          >
            Análisis
          </button>
          <button
            className={activeTab === 'projection' ? 'tab tab--active' : 'tab'}
            type="button"
            role="tab"
            aria-selected={activeTab === 'projection'}
            onClick={() => setActiveTab('projection')}
          >
            Proyección IA
          </button>
        </div>
      </nav>

      <div className="global-reminder">
        <aside className="daily-reminder" aria-label="Recordatorio diario">
          <div className="daily-reminder__content">
            <strong>Recordatorio diario</strong>
            <p className="daily-reminder__message">
              Revisa o registra tus movimientos financieros de hoy.
            </p>
            <p className="daily-reminder__explanation">
              Mantener tus movimientos al día permite que los cálculos, gráficos
              y futuras proyecciones se basen en información financiera actualizada.
            </p>
          </div>
        </aside>
      </div>

      <main className="workspace">
        {activeTab === 'movements' && (
          <div className="tab-panel" role="tabpanel">
            <section className="panel" aria-labelledby="register-title">
              <div className="panel__heading">
                <p>Nuevo registro</p>
                <h2 id="register-title">Registrar movimiento</h2>
              </div>

              <form className="movement-form" onSubmit={handleSubmit}>
                <label className="field field--wide">
                  <span>Descripción</span>
                  <input
                    type="text"
                    name="description"
                    value={description}
                    onChange={(event) => {
                      setDescription(event.target.value)
                      if (descriptionError) setDescriptionError('')
                    }}
                    placeholder="Ej: Sueldo, supermercado..."
                    aria-invalid={Boolean(descriptionError)}
                    aria-describedby={descriptionError ? 'description-error' : undefined}
                    required
                  />
                  {descriptionError && (
                    <small className="field__error" id="description-error" role="alert">
                      {descriptionError}
                    </small>
                  )}
                </label>

                <label className="field">
                  <span>Categoría</span>
                  <select
                    name="category"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                    required
                  >
                    <option value="" disabled>Selecciona una categoría</option>
                    {availableCategories.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Tipo</span>
                  <select
                    name="type"
                    value={type}
                    onChange={(event) => handleTypeChange(event.target.value as MovementType)}
                  >
                    <option>Ingreso</option>
                    <option>Gasto</option>
                  </select>
                </label>

                <label className="field">
                  <span>Monto</span>
                  <input
                    type="number"
                    name="amount"
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                    min="1"
                    step="1"
                    placeholder="0"
                    required
                  />
                </label>

                <label className="field">
                  <span>Fecha</span>
                  <input
                    type="date"
                    name="date"
                    value={date}
                    onChange={(event) => setDate(event.target.value)}
                    required
                  />
                </label>

                <div className="form-actions">
                  <button className="primary-button" type="submit">Agregar</button>
                </div>
              </form>
            </section>

            <section className="budget-panel" aria-labelledby="budget-edit-title">
              <div className="budget-panel__heading">
                <div>
                  <p>Planificación personal</p>
                  <h2 id="budget-edit-title">Presupuesto personal</h2>
                  <span className="budget-panel__description">
                    Define cuánto deseas destinar como máximo a tus gastos.
                  </span>
                </div>
                {budget !== null && (
                  <strong>{currencyFormatter.format(budget)}</strong>
                )}
              </div>

              <form className="budget-form" onSubmit={handleBudgetSubmit}>
                <label className="field">
                  <span>Monto planificado para gastos</span>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={budgetInput}
                    onChange={(event) => setBudgetInput(event.target.value)}
                    placeholder="Ej: 500000"
                    required
                  />
                </label>
                <button
                  className="primary-button"
                  type="submit"
                  disabled={isBudgetSaving}
                >
                  {isBudgetSaving
                    ? 'Guardando...'
                    : budget === null
                      ? 'Guardar presupuesto'
                      : 'Actualizar presupuesto'}
                </button>
              </form>

              {budgetError && (
                <div className="budget-message budget-message--error" role="alert">
                  {budgetError}
                </div>
              )}
              {budgetSuccess && (
                <div className="budget-message budget-message--success" role="status">
                  {budgetSuccess}
                </div>
              )}
            </section>

            <section className="panel movements-panel" aria-labelledby="movements-title">
              <div className="panel__heading">
                <p>Historial temporal</p>
                <h2 id="movements-title">Movimientos registrados</h2>
              </div>

              {communicationError && (
                <div className="analysis-message" role="alert">
                  {communicationError}
                </div>
              )}

              <div className="history-filters" aria-label="Filtros del historial">
                <label className="field">
                  <span>Consultar por</span>
                  <select
                    value={dateFilter}
                    onChange={(event) => setDateFilter(event.target.value as DateFilter)}
                  >
                    <option value="all">Todos los movimientos</option>
                    <option value="day">Día</option>
                    <option value="week">Semana</option>
                    <option value="month">Mes</option>
                    <option value="range">Rango personalizado</option>
                  </select>
                </label>

                {(dateFilter === 'day' || dateFilter === 'week') && (
                  <label className="field">
                    <span>{dateFilter === 'day' ? 'Fecha' : 'Fecha de referencia'}</span>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(event) => setSelectedDate(event.target.value)}
                    />
                  </label>
                )}

                {dateFilter === 'month' && (
                  <label className="field">
                    <span>Mes</span>
                    <input
                      type="month"
                      value={selectedMonth}
                      onChange={(event) => setSelectedMonth(event.target.value)}
                    />
                  </label>
                )}

                {dateFilter === 'range' && (
                  <>
                    <label className="field">
                      <span>Fecha inicial</span>
                      <input
                        type="date"
                        value={rangeStart}
                        max={rangeEnd || undefined}
                        onChange={(event) => setRangeStart(event.target.value)}
                      />
                    </label>
                    <label className="field">
                      <span>Fecha final</span>
                      <input
                        type="date"
                        value={rangeEnd}
                        min={rangeStart || undefined}
                        onChange={(event) => setRangeEnd(event.target.value)}
                      />
                    </label>
                  </>
                )}
              </div>

              {movements.length === 0 ? (
                <div className="empty-state">
                  <span aria-hidden="true">$</span>
                  <p>Aún no existen movimientos registrados.</p>
                </div>
              ) : filteredMovements.length === 0 ? (
                <div className="empty-state">
                  <span aria-hidden="true">$</span>
                  <p>No se encontraron movimientos para el filtro seleccionado.</p>
                </div>
              ) : (
                <div className="history-table">
                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          <th>Descripción</th>
                          <th>Categoría</th>
                          <th>Tipo</th>
                          <th>Monto</th>
                          <th>Fecha</th>
                          <th>Acción</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedMovements.map((movement) => (
                          <tr key={movement.id}>
                            <td>{movement.description}</td>
                            <td>{movement.category}</td>
                            <td>
                              <span className={`type-badge type-badge--${movement.type.toLowerCase()}`}>
                                {movement.type}
                              </span>
                            </td>
                            <td className={movement.type === 'Ingreso' ? 'amount--income' : 'amount--expense'}>
                              {movement.type === 'Ingreso' ? '+' : '-'}
                              {currencyFormatter.format(movement.amount)}
                            </td>
                            <td>{movement.date}</td>
                            <td>
                              <button
                                className="delete-button"
                                type="button"
                                onClick={() => removeMovement(movement.id)}
                                aria-label={`Eliminar movimiento ${movement.description}`}
                              >
                                Eliminar
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="pagination-controls" aria-label="Paginación del historial">
                    <label className="pagination-size">
                      <span>Movimientos por página</span>
                      <select
                        value={movementsPerPage}
                        onChange={(event) => {
                          setMovementsPerPage(Number(event.target.value))
                          setCurrentPage(1)
                        }}
                      >
                        <option value="10">10</option>
                        <option value="20">20</option>
                        <option value="30">30</option>
                      </select>
                    </label>

                    <div className="pagination-navigation">
                      <button
                        type="button"
                        onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                        disabled={safeCurrentPage === 1}
                      >
                        Anterior
                      </button>
                      <span>Página {safeCurrentPage} de {totalPages}</span>
                      <button
                        type="button"
                        onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                        disabled={safeCurrentPage === totalPages}
                      >
                        Siguiente
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </section>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="tab-panel" role="tabpanel">
            <section className="view-heading">
              <p>Estado financiero</p>
              <h2>Análisis</h2>
            </section>

            <section className="budget-panel" aria-labelledby="budget-title">
              <div className="budget-panel__heading">
                <div>
                  <p>Planificación personal</p>
                  <h3 id="budget-title">Presupuesto personal</h3>
                </div>
                {budget !== null && (
                  <strong>{currencyFormatter.format(budget)}</strong>
                )}
              </div>

              {budget === null ? (
                <p className="budget-empty">
                  Aún no has definido un presupuesto personal.
                </p>
              ) : (
                <div className="budget-metrics" aria-label="Seguimiento del presupuesto">
                  <article>
                    <span>Presupuesto</span>
                    <strong>{currencyFormatter.format(budget)}</strong>
                  </article>
                  <article>
                    <span>Gastos del período</span>
                    <strong>{currencyFormatter.format(summary.totalExpenses)}</strong>
                  </article>
                  <article>
                    <span>Ejecución del presupuesto</span>
                    <strong>{budgetExecution?.toFixed(1)}%</strong>
                  </article>
                </div>
              )}
            </section>

            <section className="summary-grid" aria-label="Indicadores financieros">
              <article className="summary-card summary-card--income">
                <p>Total ingresos</p>
                <strong>{currencyFormatter.format(summary.totalIncome)}</strong>
              </article>
              <article className="summary-card summary-card--expense">
                <p>Total gastos</p>
                <strong>{currencyFormatter.format(summary.totalExpenses)}</strong>
              </article>
              <article className="summary-card summary-card--balance">
                <p>Balance</p>
                <strong>{currencyFormatter.format(summary.balance)}</strong>
              </article>
              <article className="summary-card summary-card--budget">
                <p>Gasto sobre ingresos</p>
                <strong>{summary.budgetUsed.toFixed(1)}%</strong>
              </article>
            </section>

            {filteredMovements.length === 0 && (
              <div className="analysis-message">
                {movements.length === 0
                  ? 'Registra movimientos para visualizar el análisis financiero.'
                  : 'No existen movimientos para el período seleccionado.'}
              </div>
            )}

            <div className="dashboard-charts">
              <section className="chart-panel" aria-labelledby="comparison-title">
                <div className="chart-panel__heading">
                  <p>Vista comparativa</p>
                  <h3 id="comparison-title">Comparación de ingresos y gastos</h3>
                </div>
                <div className="vertical-bar-chart" aria-label="Gráfico de ingresos y gastos">
                  <div className="vertical-bar-chart__plot">
                    <div className="vertical-bar-item">
                      <strong>{currencyFormatter.format(summary.totalIncome)}</strong>
                      <div className="vertical-bar-track">
                        <div
                          className="vertical-bar vertical-bar--income"
                          style={{ height: `${incomeBarHeight}%` }}
                        />
                      </div>
                      <span>Ingresos</span>
                    </div>
                    <div className="vertical-bar-item">
                      <strong>{currencyFormatter.format(summary.totalExpenses)}</strong>
                      <div className="vertical-bar-track">
                        <div
                          className="vertical-bar vertical-bar--expense"
                          style={{ height: `${expenseBarHeight}%` }}
                        />
                      </div>
                      <span>Gastos</span>
                    </div>
                  </div>
                </div>
              </section>

              <section className="chart-panel" aria-labelledby="categories-title">
                <div className="chart-panel__heading">
                  <p>Distribución</p>
                  <h3 id="categories-title">Gastos por categoría</h3>
                </div>
                {expensesByCategory.length === 0 ? (
                  <div className="analysis-message">
                    No existen gastos para el período seleccionado.
                  </div>
                ) : (
                  <div className="donut-chart-layout">
                    <div
                      className="donut-chart"
                      style={{ background: expenseDonutGradient }}
                      role="img"
                      aria-label="Distribución porcentual de gastos por categoría"
                    >
                      <div className="donut-chart__center">
                        <span>Total gastos</span>
                        <strong>{currencyFormatter.format(summary.totalExpenses)}</strong>
                      </div>
                    </div>
                    <div className="donut-legend">
                      {expensesByCategory.map((categoryItem, index) => (
                        <div className="donut-legend__item" key={categoryItem.name}>
                          <span
                            className="donut-legend__color"
                            style={{ backgroundColor: categoryColors[index % categoryColors.length] }}
                            aria-hidden="true"
                          />
                          <div>
                            <span>{categoryItem.name}</span>
                            <strong>
                              {currencyFormatter.format(categoryItem.total)} · {categoryItem.percentage.toFixed(1)}%
                            </strong>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            </div>

            <section className="chart-panel" aria-labelledby="trend-title">
              <div className="chart-panel__heading">
                <p>Evolución temporal</p>
                <h3 id="trend-title">Evolución de gastos por fecha</h3>
              </div>
              {expensesByDate.length === 0 ? (
                <div className="analysis-message">
                  No existen gastos para visualizar en el período seleccionado.
                </div>
              ) : (
                <div className="trend-chart">
                  <div className="trend-chart__scroll">
                    <svg
                      className="trend-chart__svg"
                      viewBox={`0 0 ${trendChartWidth} ${trendChartHeight}`}
                      style={{ minWidth: `${trendChartWidth}px` }}
                      role="img"
                      aria-label="Gastos agrupados por fecha"
                    >
                      {trendScalePositions.map((position) => {
                        const y = trendChartHeight
                          - trendChartBottomPadding
                          - position * trendAvailableHeight

                        return (
                          <g key={position}>
                            <line
                              className="trend-grid-line"
                              x1={trendChartLeftPadding}
                              x2={trendChartWidth - trendChartRightPadding}
                              y1={y}
                              y2={y}
                            />
                            <text
                              className="trend-axis-value"
                              x={trendChartLeftPadding - 12}
                              y={y + 4}
                              textAnchor="end"
                            >
                              {compactCurrencyFormatter.format(trendDataMaximum * position)}
                            </text>
                          </g>
                        )
                      })}
                      {expensesByDate.map((item, index) => {
                        const groupCenter = trendChartLeftPadding
                          + trendGroupWidth * (index + 0.5)
                        const expenseHeight = (item.total / trendMaximum) * trendAvailableHeight
                        const chartBottom = trendChartHeight - trendChartBottomPadding
                        const barTop = chartBottom - expenseHeight

                        return (
                          <g key={item.date}>
                            <rect
                              className="trend-bar--expense"
                              x={groupCenter - trendBarWidth / 2}
                              y={barTop}
                              width={trendBarWidth}
                              height={expenseHeight}
                              rx="4"
                            >
                              <title>{`${formatMovementDate(item.date)}: gastos ${currencyFormatter.format(item.total)}`}</title>
                            </rect>
                            <text
                              className="trend-amount-label"
                              x={groupCenter}
                              y={Math.max(trendChartTopPadding - 7, barTop - 7)}
                              textAnchor="middle"
                            >
                              {compactCurrencyFormatter.format(item.total)}
                            </text>
                            <text
                              className="trend-date-label"
                              x={groupCenter}
                              y={trendChartHeight - 16}
                              textAnchor="middle"
                            >
                              {formatMovementDate(item.date)}
                            </text>
                          </g>
                        )
                      })}
                    </svg>
                  </div>
                </div>
              )}
            </section>
          </div>
        )}

        {activeTab === 'projection' && (
          <div className="tab-panel" role="tabpanel">
            <section className="projection-panel">
              <div className="projection-panel__badge">IA</div>
              <p>Módulo en preparación</p>
              <h2>Proyección IA</h2>
              <p className="projection-panel__description">
                La proyección IA permitirá estimar gasto futuro, balance esperado
                y riesgo de superar el presupuesto a partir del historial financiero
                del usuario.
              </p>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
