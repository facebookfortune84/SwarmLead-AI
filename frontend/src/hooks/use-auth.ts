"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  clearTokens,
  saveTokens,
} from "@/lib/auth";

export interface LoginPayload {
  email: string;

  password: string;
}

export function useLogin() {
  return useMutation({
    mutationFn: async (
      payload: LoginPayload
    ) => {
      const response =
        await api.post(
          "/api/auth/login",
          payload
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
      try {
        await api.post(
          "/api/auth/logout"
        );
      } finally {
        clearTokens();
      }
    },

    onSettled: () => {
      clearTokens();

      window.location.assign(
        "/login"
      );
    },
  });
}