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

export interface ProductDetails {
  brand?: string
  barcode?: string
  variant?: string
  fat_percent?: string | null
  package_size?: string | null
  package_unit?: string
}

export interface ReceiptLine extends ProductDetails {
  name: string
  promotion_condition?: string
  quantity: string | null
  unit: string
  unit_price: string | null
  discount: string | null
  line_total: string | null
  line_total_is_net: boolean | null
  category_id: string | null
  allocated_amount?: string
}

export interface ReceiptDraft {
  merchant: string
  branch?: string
  branch_address?: string
  purchase_date: string | null
  receipt_number: string
  currency: 'KZT'
  paid: string | null
  order_discount: string
  fees: string
  confirm_paid: boolean
  items: ReceiptLine[]
}

export interface ReceiptTotals {
  subtotal: string
  item_discounts: string
  order_discount: string
  fees: string
  calculated: string
  paid: string | null
  difference: string | null
  line_amounts: string[]
}

export interface SavedReceipt extends ReceiptDraft {
  totals: ReceiptTotals
}

export interface ExtractedReceipt {
  merchant: string | null
  branch?: string | null
  branch_address?: string | null
  purchase_date: string | null
  receipt_number: string | null
  currency: string | null
  paid: number | null
  order_discount: number | null
  fees: number | null
  uncertain_fields: string[]
  items: Array<{
    name: string | null
    brand?: string | null
    barcode?: string | null
    variant?: string | null
    fat_percent?: number | null
    package_size?: number | null
    package_unit?: string | null
    promotion_condition?: string | null
    quantity: number | null
    unit: string | null
    unit_price: number | null
    discount: number | null
    line_total: number | null
    line_total_is_net: boolean | null
    suggested_category: string | null
    uncertain_fields: string[]
  }>
}

export interface ReceiptReport {
  total: string
  merchants: { name: string | null; total: string }[]
  categories: CategoryBreakdown[]
  highest_category: CategoryBreakdown | null
  budgets: {
    category_name: string | null
    date_from: string
    date_to: string
    limit: string
    spent: string
    remaining: string
  }[]
  previous_total: string | null
  change: string | null
  change_pct: string | null
}

export interface TransactionCreate {
  client_request_id?: string
  category_id?: string | null
  amount: number
  type: TransactionType
  description: string | null
  merchant?: string | null
  transaction_date: string
  tags?: string[]
}

export interface ReceiptDetails {
  total: number | null
  currency: string | null
  merchant: string | null
  purchase_date: string | null
}

export interface ImageAnalysis {
  reply: string
  receipt: ReceiptDetails | null
  receipt_request_id: string | null
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
