"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  CheckoutCreate,
  CheckoutSessionResponse,
} from "@/types/stripe";

export function useCreateCheckoutSession() {
  return useMutation<
    CheckoutSessionResponse,
    Error,
    CheckoutCreate
  >({
    mutationFn: async (
      payload
    ) => {
      const response =
        await api.post(
          "/api/stripe/create-checkout-session",
          payload
        );

      return response.data;
    },
  });
}