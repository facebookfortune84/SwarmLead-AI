import axios from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  saveTokens,
} from "./auth";

const API_URL =
  process.env
    .NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export const api =
  axios.create({
    baseURL: API_URL,
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
      `${API_URL}/api/auth/refresh`,
      {
        refresh_token:
          refreshToken,
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
    
    console.log(
      "API ERROR",
      status,
      originalRequest?.url
    );

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