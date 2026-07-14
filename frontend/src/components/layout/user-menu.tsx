"use client";

import { Button } from "@/components/ui/button";

import {
  useCurrentUser,
} from "@/hooks/use-current-user";

import {
  useLogout,
} from "@/hooks/use-auth";

export function UserMenu() {
  const {
    data,
  } = useCurrentUser();

  const logout =
    useLogout();

  if (!data) {
    return (
      <Button
        size="sm"
        variant="outline"
        onClick={() =>
          (window.location.href =
            "/login")
        }
      >
        Login
      </Button>
    );
  }

  return (
    <div className="space-y-2">
      <div className="text-sm">
        {data.full_name ??
          data.email}
      </div>

      <Button
        size="sm"
        variant="outline"
        onClick={() =>
          logout.mutate()
        }
      >
        Logout
      </Button>
    </div>
  );
}