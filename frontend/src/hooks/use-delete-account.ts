"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  clearTokens,
} from "@/lib/auth";

export function useDeleteAccount() {
  return useMutation({
    mutationFn: async () => {
      const response =
        await api.delete(
          "/api/users/me"
        );

      return response.data;
    },

    onSuccess: () => {
      clearTokens();

      window.location.assign(
        "/login"
      );
    },
  });
}