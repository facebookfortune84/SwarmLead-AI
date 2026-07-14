"use client";

import { useState } from "react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function CampaignBuilder() {
  const [name, setName] =
    useState("");

  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Campaign Builder
      </h2>

      <div className="mt-4 flex gap-2">
        <Input
          value={name}
          placeholder="Campaign Name"
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
        />

        <Button>
          Create
        </Button>
      </div>
    </Card>
  );
}