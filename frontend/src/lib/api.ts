import axios from "axios";

import {
  getAccessToken,
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
  (error) => {
    if (
      error?.response
        ?.status === 401
    ) {
      console.warn(
        "Authentication required."
      );
    }

    return Promise.reject(
      error
    );
  }
);