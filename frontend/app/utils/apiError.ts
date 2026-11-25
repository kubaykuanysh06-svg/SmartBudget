export function getErrorStatus(err: any): number | undefined {
  return err?.statusCode ?? err?.status ?? err?.response?.status
}

export function formatApiError(err: any, fallback = 'Произошла ошибка при выполнении запроса'): string {
  const detail = err?.data?.detail ?? err?.response?._data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    if (detail === 'Email already registered') return 'Этот email уже зарегистрирован'
    if (detail === 'Invalid email or password') return 'Неверный email или пароль'
    if (detail === 'Category not found') return 'Выбранная категория не найдена'
    if (detail === 'Gemini API key is not configured') {
      return 'Для работы ИИ укажите действительный GEMINI_API_KEY в backend/.env'
    }
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    const field = String(first?.loc?.[first.loc.length - 1] || '')
    const type = String(first?.type || '')
    if (field === 'amount' || field === 'limit_amount') {
      if (type.includes('greater_than')) return 'Сумма должна быть больше 0'
      if (type.includes('less_than_equal') || type.includes('max_digits')) {
        return 'Сумма превышает допустимый максимум (999 999 999 999,99)'
      }
      if (type.includes('decimal_places')) {
        return 'Укажите не более 2 знаков после запятой'
      }
      return 'Введите корректную положительную сумму'
    }
    if (field === 'password') {
      return 'Пароль должен содержать от 8 символов (не более 72 байт UTF-8)'
    }
    if (field === 'email') {
      return 'Введите корректный email адрес'
    }
    if (typeof first?.msg === 'string') return first.msg
  }
  return fallback
}

export function validateMoneyInput(value: unknown): string | null {
  if (value === '' || value === null || value === undefined) {
    return 'Введите сумму больше 0'
  }
  const num = typeof value === 'number' ? value : Number(String(value).replace(',', '.'))
  if (!Number.isFinite(num) || num <= 0) {
    return 'Сумма должна быть положительным числом больше 0'
  }
  if (num > 999999999999.99) {
    return 'Сумма превышает допустимый максимум (999 999 999 999,99)'
  }
  const raw = String(value).trim().replace(',', '.')
  if (/^\d+\.\d{3,}$/.test(raw)) {
    return 'Укажите не более 2 знаков после запятой'
  }
  return null
}
