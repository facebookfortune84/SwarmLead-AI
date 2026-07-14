"use client";

import { useState } from "react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useCreateLead } from "@/hooks/use-create-lead";

export function LeadCreateDialog() {
  const [open, setOpen] =
    useState(false);

  const [email, setEmail] =
    useState("");

  const [name, setName] =
    useState("");

  const [company, setCompany] =
    useState("");

  const createLead =
    useCreateLead();

  async function handleSave() {
    if (!email.trim()) {
      return;
    }

    await createLead.mutateAsync({
      email,
      name,
      company,
    });

    setEmail("");
    setName("");
    setCompany("");

    setOpen(false);
  }

  return (
    <Dialog
      open={open}
      onOpenChange={setOpen}
    >
      <DialogTrigger
        className="
          inline-flex
          items-center
          justify-center
          rounded-md
          px-4
          py-2
          text-sm
          font-medium
          bg-primary
          text-primary-foreground
          hover:opacity-90
        "
      >
        Create Lead
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Create Lead
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Name"
            value={name}
            onChange={(e) =>
              setName(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Company"
            value={company}
            onChange={(e) =>
              setCompany(
                e.target.value
              )
            }
          />

          <Button
            className="w-full"
            onClick={handleSave}
            disabled={
              createLead.isPending
            }
          >
            {createLead.isPending
              ? "Saving..."
              : "Save Lead"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}