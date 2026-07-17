"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

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
  const queryClient =
    useQueryClient();

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

    onSuccess: async (
      data
    ) => {
      saveTokens(
        data.access_token,
        data.refresh_token
      );

      await queryClient.invalidateQueries(
        {
          queryKey: [
            "current-user",
          ],
        }
      );

      await queryClient.refetchQueries(
        {
          queryKey: [
            "current-user",
          ],
        }
      );
    },
  });
}

export function useLogout() {
  const queryClient =
    useQueryClient();

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

    onSettled: async () => {
      clearTokens();

      queryClient.clear();

      window.location.assign(
        "/login"
      );
    },
  });
}