"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useLogin } from "@/hooks/use-auth";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const login = useLogin();

  async function submit() {
    try {
      const result =
        await login.mutateAsync({
          email,
          password,
        });

      console.log(
        "LOGIN SUCCESS",
        result
      );

      console.log(
        "TOKEN EXISTS",
        !!localStorage.getItem(
          "swarmlead_access_token"
        )
      );

      router.replace(
        "/dashboard"
      );
    } catch (error) {
      console.error(
        "LOGIN FAILURE",
        error
      );
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md p-6">
        <h1 className="mb-6 text-2xl font-bold">
          Sign In
        </h1>

        <div className="space-y-4">
          <Input
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />

          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(
                e.target.value
              )
            }
          />

          <Button
            className="w-full"
            onClick={submit}
            disabled={
              login.isPending
            }
          >
            {login.isPending
              ? "Signing In..."
              : "Sign In"}
          </Button>
        </div>
      </Card>
    </div>
  );
}