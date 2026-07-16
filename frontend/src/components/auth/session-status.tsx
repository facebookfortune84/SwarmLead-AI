"use client";

import {
  useAuthVerify,
} from "@/hooks/use-auth-verify";

export function SessionStatus() {
  const {
    isLoading,
    isError,
  } =
    useAuthVerify();

  if (isLoading) {
    return (
      <div className="text-xs text-muted-foreground">
        Checking Session...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-xs text-red-500">
        Session Invalid
      </div>
    );
  }

  return (
    <div className="text-xs text-green-600">
      Session Active
    </div>
  );
}