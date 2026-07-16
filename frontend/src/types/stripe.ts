export interface CheckoutCreate {
  product_name?: string;

  amount_cents?: number;

  price_id?: string;
}

export interface CheckoutSessionResponse {
  id: string;

  url: string;
}