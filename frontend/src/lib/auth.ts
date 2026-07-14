const ACCESS_TOKEN_KEY =
  "swarmlead_access_token";

const REFRESH_TOKEN_KEY =
  "swarmlead_refresh_token";

export function getAccessToken() {
  if (typeof window === "undefined")
    return null;

  return localStorage.getItem(
    ACCESS_TOKEN_KEY
  );
}

export function getRefreshToken() {
  if (typeof window === "undefined")
    return null;

  return localStorage.getItem(
    REFRESH_TOKEN_KEY
  );
}

export function saveTokens(
  accessToken: string,
  refreshToken?: string
) {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    accessToken
  );

  if (refreshToken) {
    localStorage.setItem(
      REFRESH_TOKEN_KEY,
      refreshToken
    );
  }
}

export function clearTokens() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );

  localStorage.removeItem(
    REFRESH_TOKEN_KEY
  );
}

export function isAuthenticated() {
  return !!getAccessToken();
}