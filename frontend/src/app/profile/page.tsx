"use client";

import { useEffect } from "react";

import { AppShell } from "@/components/layout/app-shell";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  useForm,
} from "react-hook-form";

import {
  useProfile,
} from "@/hooks/use-profile";

import {
  useUpdateProfile,
} from "@/hooks/use-update-profile";

import {
  useDeleteAccount,
} from "@/hooks/use-delete-account";

interface FormValues {
  full_name: string;

  email: string;
}

export default function ProfilePage() {
  const {
    data,
    isLoading,
  } =
    useProfile();

  const updateProfile =
    useUpdateProfile();

  const deleteAccount =
    useDeleteAccount();

  const {
    register,
    handleSubmit,
    reset,
  } =
    useForm<FormValues>();

  useEffect(() => {
    if (data) {
      reset({
        full_name:
          data.full_name,

        email:
          data.email,
      });
    }
  }, [
    data,
    reset,
  ]);

  async function save(
    values: FormValues
  ) {
    await updateProfile.mutateAsync(
      values
    );
  }

  if (isLoading) {
    return (
      <AppShell>
        Loading...
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            My Profile
          </h1>

          <p className="text-muted-foreground">
            Account management
            and preferences.
          </p>
        </div>

        <Card className="p-6">
          <form
            onSubmit={handleSubmit(
              save
            )}
            className="space-y-4"
          >
            <Input
              {...register(
                "full_name"
              )}
            />

            <Input
              {...register(
                "email"
              )}
            />

            <div className="rounded-lg border p-4">
              <div>
                Role:
                {" "}
                {
                  data?.role
                }
              </div>

              <div>
                Subscription:
                {" "}
                {
                  data?.subscription_tier
                }
              </div>

              <div>
                Active:
                {" "}
                {String(
                  data?.is_active
                )}
              </div>
            </div>

            <Button
              type="submit"
              disabled={
                updateProfile.isPending
              }
            >
              Save Profile
            </Button>
          </form>
        </Card>

        <Card className="border-red-500 p-6">
          <h2 className="font-semibold text-red-600">
            Danger Zone
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            Deleting your account
            will permanently disable access.
          </p>

          <Button
            className="mt-4"
            variant="destructive"
            onClick={() =>
              deleteAccount.mutate()
            }
          >
            Delete Account
          </Button>
        </Card>
      </div>
    </AppShell>
  );
}