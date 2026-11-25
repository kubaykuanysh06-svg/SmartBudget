export type TransactionType = 'income' | 'expense' | 'transfer'

export interface User {
  id: string
  email: string
  name: string
  currency: string
  created_at: string
}

export interface Category {
  id: string
  user_id?: string | null
  parent_id?: string | null
  name: string
  icon: string
  color: string
  type: 'income' | 'expense'
  is_system: boolean
}

export interface CategoryTree extends Category {
  children: CategoryTree[]
}

export interface Transaction {
  id: string
  user_id: string
  category_id: string | null
  category?: Category
  amount: number
  type: TransactionType
  description: string | null
  merchant?: string | null
  transaction_date: string
  tags?: string[]
  receipt_url?: string | null
  ai_metadata?: Record<string, any>
  created_at: string
}

export interface TransactionCreate {
  category_id?: string | null
  amount: number
  type: TransactionType
  description: string | null
  merchant?: string | null
  transaction_date: string
  tags?: string[]
}

export interface Budget {
  id: string
  user_id: string
  category_id?: string | null
  category?: Category
  limit_amount: number
  period: 'weekly' | 'monthly' | 'yearly'
  start_date: string
  end_date?: string | null
  is_active: boolean
}

export interface BudgetStatus extends Budget {
  spent: number
  remaining: number
  percentage: number
}

export interface SummaryAnalytics {
  total_income: number
  total_expense: number
  net: number
  transactions_count: number
}

export interface CategoryBreakdown {
  category_id: string | null
  category_name: string | null
  total: number
  percentage: number
}

export interface TrendPoint {
  month: string
  income: number
  expense: number
}

export interface Deal {
  id: string
  title: string
  description?: string
  store: string
  url?: string
  original_price: number
  discount_price: number
  discount_percent: number
  category_id?: string
  valid_from?: string
  valid_until?: string
  source: string
  is_active: boolean
}

export interface AiInsight {
  id: string
  user_id: string
  type: 'tip' | 'warning' | 'recommendation' | 'deal'
  title: string
  content: string
  metadata?: Record<string, any>
  is_read: boolean
  created_at: string
}

export interface PriceAnalysis {
  verdict: 'good_deal' | 'fair' | 'overpriced'
  estimated_fair_price?: number | null
  savings_or_overpay?: number | null
  explanation: string
}
