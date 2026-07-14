"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  saveTokens,
  clearTokens,
} from "@/lib/auth";

export function useLogin() {
  return useMutation({
    mutationFn: async ({
      email,
      password,
    }: {
      email: string;
      password: string;
    }) => {
      const response =
        await api.post(
          "/api/auth/login",
          {
            email,
            password,
          }
        );

      return response.data;
    },

    onSuccess: (data) => {
      saveTokens(
        data.access_token,
        data.refresh_token
      );
    },
  });
}

export function useLogout() {
  return useMutation({
    mutationFn: async () => {
      await api.post(
        "/api/auth/logout"
      );
    },

    onSettled: () => {
      clearTokens();
    },
  });
}