"use client";

import {
  ReactNode,
} from "react";

import {
  Permission,
} from "@/types/rbac";

import {
  useCurrentUser,
} from "@/hooks/use-current-user";

import {
  hasPermission,
} from "@/lib/permissions";

interface Props {
  permission: Permission;

  children: ReactNode;

  fallback?: ReactNode;
}

export function PermissionGate({
  permission,
  children,
  fallback = null,
}: Props) {
  const {
    data,
    isLoading,
  } =
    useCurrentUser();

  if (
    isLoading
  ) {
    return null;
  }

  if (
    !data
  ) {
    return <>{fallback}</>;
  }

  if (
    !hasPermission(
      data.role,
      permission
    )
  ) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}