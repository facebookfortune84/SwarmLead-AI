"use client";

import {
  useEffect,
} from "react";

import {
  useForm,
} from "react-hook-form";

import { User } from "@/types/user";

import {
  useUpdateUser,
} from "@/hooks/use-update-user";

import { Button } from "@/components/ui/button";

import { Input } from "@/components/ui/input";

import { Card } from "@/components/ui/card";

interface Props {
  user: User;

  onClose: () => void;
}

interface FormValues {
  full_name: string;

  email: string;
}

export function UserEditDialog({
  user,
  onClose,
}: Props) {
  const updateUser =
    useUpdateUser();

  const {
    register,
    handleSubmit,
    reset,
  } =
    useForm<FormValues>();

  useEffect(() => {
    reset({
      full_name:
        user.full_name,

      email:
        user.email,
    });
  }, [
    user,
    reset,
  ]);

  async function submit(
    values: FormValues
  ) {
    await updateUser.mutateAsync(
      {
        userId:
          user.id,

        ...values,
      }
    );

    onClose();
  }

  return (
    <Card className="p-6">
      <form
        onSubmit={handleSubmit(
          submit
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

        <div className="flex gap-2">
          <Button
            type="submit"
          >
            Save
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={onClose}
          >
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}