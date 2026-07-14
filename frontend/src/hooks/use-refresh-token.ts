"use client";

import { api } from "@/lib/api";

import {
  getRefreshToken,
  saveTokens,
} from "@/lib/auth";

export async function refreshToken() {
  const refreshTokenValue =
    getRefreshToken();

  if (!refreshTokenValue) {
    throw new Error(
      "Missing refresh token"
    );
  }

  const response =
    await api.post(
      "/api/auth/refresh",
      {
        refresh_token:
          refreshTokenValue,
      }
    );

  saveTokens(
    response.data.access_token,
    refreshTokenValue
  );

  return response.data;
}