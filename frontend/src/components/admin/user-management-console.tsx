"use client";

import {
  useMemo,
  useState,
} from "react";

import {
  useUsers,
} from "@/hooks/use-users";

import {
  UserSearch,
} from "./user-search";

import {
  UserTable,
} from "./user-table";

import {
  AdminStats,
} from "./admin-stats";

export function UserManagementConsole() {
  const [
    search,
    setSearch,
  ] = useState("");

  const {
    data = [],
    isLoading,
  } = useUsers();

  const filtered =
    useMemo(() => {
      const term =
        search.toLowerCase();

      return data.filter(
        (
          user
        ) =>
          user.full_name
            .toLowerCase()
            .includes(
              term
            ) ||
          user.email
            .toLowerCase()
            .includes(
              term
            )
      );
    }, [
      data,
      search,
    ]);

  if (isLoading) {
    return (
      <div>
        Loading...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AdminStats
        users={data}
      />

      <UserSearch
        value={search}
        onChange={setSearch}
      />

      <UserTable
        users={filtered}
      />
    </div>
  );
}