export interface CheckoutCreate {
  product_name?: string;

  amount_cents?: number;

  price_id?: string;

  /** "monthly" (default) or "annual" — annual is billed at 10x monthly (2 months free). */
  billing?: "monthly" | "annual";
}

export interface CheckoutSessionResponse {
  id: string;

  url: string;
}