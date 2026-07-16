"use client";

import { Card } from "@/components/ui/card";

export function AdminPanel() {
  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Administration Panel
      </h2>

      <p className="mt-2 text-sm text-muted-foreground">
        Administrative tools are available
        through the Admin Console.
      </p>
    </Card>
  );
}