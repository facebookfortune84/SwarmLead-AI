"use client";

import { Button } from "@/components/ui/button";

import { User } from "@/types/user";

import {
  useActivateUser,
} from "@/hooks/use-activate-user";

import {
  useSuspendUser,
} from "@/hooks/use-suspend-user";

import {
  useDeleteUser,
} from "@/hooks/use-delete-user";

interface Props {
  users: User[];
}

export function UserTable({
  users,
}: Props) {
  const suspend =
    useSuspendUser();

  const activate =
    useActivateUser();

  const remove =
    useDeleteUser();

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="p-4 text-left">
              Name
            </th>

            <th className="p-4 text-left">
              Email
            </th>

            <th className="p-4 text-left">
              Role
            </th>

            <th className="p-4 text-left">
              Active
            </th>

            <th className="p-4 text-left">
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {users.map(
            (user) => (
              <tr
                key={user.id}
                className="border-b"
              >
                <td className="p-4">
                  {
                    user.full_name
                  }
                </td>

                <td className="p-4">
                  {
                    user.email
                  }
                </td>

                <td className="p-4">
                  {user.role}
                </td>

                <td className="p-4">
                  {String(
                    user.is_active
                  )}
                </td>

                <td className="p-4">
                  <div className="flex gap-2">
                    {user.is_active ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          suspend.mutate(
                            user.id
                          )
                        }
                      >
                        Suspend
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() =>
                          activate.mutate(
                            user.id
                          )
                        }
                      >
                        Activate
                      </Button>
                    )}

                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() =>
                        remove.mutate(
                          user.id
                        )
                      }
                    >
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}