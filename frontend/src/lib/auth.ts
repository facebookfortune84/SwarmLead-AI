export const ACCESS_TOKEN_KEY =
  "swarmlead_access_token";

export const REFRESH_TOKEN_KEY =
  "swarmlead_refresh_token";

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

export function getAccessToken():
  string | null {
  if (
    typeof window ===
    "undefined"
  ) {
    return null;
  }

  return localStorage.getItem(
    ACCESS_TOKEN_KEY
  );
}

export function getRefreshToken():
  string | null {
  if (
    typeof window ===
    "undefined"
  ) {
    return null;
  }

  return localStorage.getItem(
    REFRESH_TOKEN_KEY
  );
}

export function saveTokens(
  accessToken: string,
  refreshToken: string
) {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    accessToken
  );

  localStorage.setItem(
    REFRESH_TOKEN_KEY,
    refreshToken
  );
}

export function clearTokens() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );

  localStorage.removeItem(
    REFRESH_TOKEN_KEY
  );
}

export function hasAccessToken() {
  return !!getAccessToken();
}

export function restoreSession() {
  return {
    accessToken:
      getAccessToken(),

    refreshToken:
      getRefreshToken(),

    authenticated:
      !!getAccessToken(),
  };
}