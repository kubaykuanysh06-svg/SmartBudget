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
  category_id: string
  category?: Category
  amount: number
  type: TransactionType
  description: string
  merchant?: string | null
  transaction_date: string
  tags?: string[]
  receipt_url?: string | null
  ai_metadata?: Record<string, any>
  created_at: string
}

export interface TransactionCreate {
  category_id: string
  amount: number
  type: TransactionType
  description: string
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

export interface BudgetStatus {
  budget: Budget
  spent: number
  remaining: number
  percentage: number
}

export interface SummaryAnalytics {
  total_income: number
  total_expense: number
  net_savings: number
  savings_rate: number
  period: string
}

export interface CategoryBreakdown {
  category_id: string
  category_name: string
  category_color: string
  total_amount: number
  percentage: number
  count: number
}

export interface TrendPoint {
  date: string
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
