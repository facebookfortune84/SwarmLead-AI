"use client";

import {
  isAuthenticated,
} from "@/lib/auth";

export function AuthGuard({
  children,
}: {
  children: React.ReactNode;
}) {
  if (
    typeof window !==
      "undefined" &&
    !isAuthenticated()
  ) {
    window.location.href =
      "/login";

    return null;
  }

  return children;
}