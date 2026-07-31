import axios from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  saveTokens,
} from "./auth";

export const api =
  axios.create({
    timeout: 30000,
  });

let refreshPromise:
  | Promise<string>
  | null = null;

async function refreshAccessToken() {
  const refreshToken =
    getRefreshToken();

  if (!refreshToken) {
    throw new Error(
      "Missing refresh token"
    );
  }

  const response =
    await axios.post(
      "/api/auth/refresh",
      {
        refresh_token:
          refreshToken,
      },
      {
        timeout: 30000,
      }
    );

  const accessToken =
    response.data
      ?.access_token;

  if (!accessToken) {
    throw new Error(
      "Refresh failed"
    );
  }

  saveTokens(
    accessToken,
    refreshToken
  );

  return accessToken;
}

api.interceptors.request.use(
  (config) => {
    const token =
      getAccessToken();

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  }
);

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest =
      error.config;

    const status =
      error?.response
        ?.status;

    if (
      status !== 401 ||
      originalRequest?._retry
    ) {
      return Promise.reject(
        error
      );
    }

    try {
      originalRequest._retry =
        true;

      if (!refreshPromise) {
        refreshPromise =
          refreshAccessToken();
      }

      const newToken =
        await refreshPromise;

      refreshPromise =
        null;

      originalRequest.headers.Authorization =
        `Bearer ${newToken}`;

      return api(
        originalRequest
      );
    } catch (
      refreshError
    ) {
      refreshPromise =
        null;

      clearTokens();

      if (
        typeof window !==
        "undefined"
      ) {
        window.location.assign(
          "/login"
        );
      }

      return Promise.reject(
        refreshError
      );
    }
  }
);