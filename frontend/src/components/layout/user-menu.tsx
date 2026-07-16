"use client";

import { Button } from "@/components/ui/button";

import {
  useCurrentUser,
} from "@/hooks/use-current-user";

import {
  useLogout,
} from "@/hooks/use-auth";

export function UserMenu() {
  const logout =
    useLogout();

  const {
    data,
    isLoading,
  } =
    useCurrentUser();

  if (isLoading) {
    return (
      <div className="text-sm text-muted-foreground">
        Loading...
      </div>
    );
  }

  if (!data) {
    return (
      <Button
        size="sm"
        variant="outline"
        onClick={() =>
          window.location.assign(
            "/login"
          )
        }
      >
        Login
      </Button>
    );
  }

  return (
    <div className="space-y-2">
      <div>
        <div className="font-medium text-sm">
          {data.full_name}
        </div>

        <div className="text-xs text-muted-foreground">
          {data.email}
        </div>

        <div className="text-xs text-muted-foreground">
          {data.role}
        </div>
      </div>

      <Button
        size="sm"
        variant="outline"
        onClick={() =>
          window.location.assign(
            "/profile"
          )
        }
      >
        Profile
      </Button>

      <Button
        size="sm"
        variant="destructive"
        onClick={() =>
          logout.mutate()
        }
      >
        Logout
      </Button>
    </div>
  );
}