export function getErrorStatus(err: any): number | undefined {
  return err?.statusCode ?? err?.status ?? err?.response?.status
}

export function formatApiError(err: any, fallback = 'Сұранысты орындау кезінде қате шықты'): string {
  const detail = err?.data?.detail ?? err?.response?._data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    if (detail === 'Email already registered') return 'Бұл email мекенжайы бұрын тіркелген'
    if (detail === 'Invalid email or password') return 'Email немесе құпиясөз қате'
    if (detail === 'Category not found') return 'Таңдалған санат табылмады'
    if (detail === 'Category type does not match transaction type') {
      return 'Санат түрі операция түріне сәйкес келмейді (кіріс не шығыс)'
    }
    if (detail === 'Budget category must be an expense category') {
      return 'Бюджет тек шығыс санатына қойылады'
    }
    if (detail === 'end_date must be on or after start_date') {
      return 'Аяқталу күні басталу күнінен ерте болмауы керек'
    }
    if (detail === 'Gemini API key is not configured') {
      return 'ЖИ қызметі үшін backend/.env файлына жарамды GEMINI_API_KEY енгізіңіз'
    }
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    const field = String(first?.loc?.[first.loc.length - 1] || '')
    const type = String(first?.type || '')
    if (field === 'amount' || field === 'limit_amount') {
      if (type.includes('greater_than')) return 'Сома 0-ден үлкен болуы керек'
      if (type.includes('less_than_equal') || type.includes('max_digits')) {
        return 'Сома рұқсат етілген шектен асып кетті (999 999 999 999,99)'
      }
      if (type.includes('decimal_places')) {
        return 'Үтірден кейін 2 таңбадан артық енгізбеңіз'
      }
      return 'Дұрыс оң сома енгізіңіз'
    }
    if (field === 'password') {
      return 'Құпиясөз кемінде 8 таңбадан тұруы керек (ең көбі 72 байт UTF-8)'
    }
    if (field === 'email') {
      return 'Дұрыс email мекенжайын енгізіңіз'
    }
    if (typeof first?.msg === 'string') return first.msg
  }
  return fallback
}

export function validateMoneyInput(value: unknown): string | null {
  if (value === '' || value === null || value === undefined) {
    return '0-ден үлкен сома енгізіңіз'
  }
  const num = typeof value === 'number' ? value : Number(String(value).replace(',', '.'))
  if (!Number.isFinite(num) || num <= 0) {
    return 'Сома 0-ден үлкен оң сан болуы керек'
  }
  if (num > 999999999999.99) {
    return 'Сома рұқсат етілген шектен асып кетті (999 999 999 999,99)'
  }
  const raw = String(value).trim().replace(',', '.')
  if (/^\d+\.\d{3,}$/.test(raw)) {
    return 'Үтірден кейін 2 таңбадан артық енгізбеңіз'
  }
  return null
}
