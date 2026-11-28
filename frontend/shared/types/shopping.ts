import type { ProductDetails } from './index'

export type Point = { lat: number; lon: number }
export type Place = Point & { name: string }
export type Area = Point & { radius: number }
export type StoreBranch = Place & { id: string; address: string; distance_km: number }
export type ProductReference = ProductDetails & { name: string }
export type Offer = {
  id: string; product: ProductReference; match: 'exact' | 'other_package' | 'similar' | 'uncertain' | 'search'
  unit: string; store: string; branch: string; address: string; distance_km: number | null; date: string
  package_price: string | null; unit_price: string | null; trip_total: string | null
  source_kind: 'receipt' | 'catalog'; source_name: string; source_url: string | null; condition: string
  current_price_verified: boolean; available_today: boolean | null; age_days: number
  /** True when the price comes from the viewer's own receipt. */
  own_receipt?: boolean; transaction_id?: string | null
}
export type Recommendation = { offer_id: string; value: string | number; compare_id: string | null; savings: string | null }
export type Comparison = {
  offers: Offer[]; catalog_available: boolean
  recommendations: Record<'cheapest_package' | 'cheapest_unit' | 'closest' | 'cheapest_with_trip', Recommendation | null>
}
