"use client";

import { Card } from "@/components/ui/card";

export function SystemHealthCard() {
  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Platform Health
      </h2>

      <div className="mt-4 space-y-3">
        <div className="flex justify-between">
          <span>
            API
          </span>

          <span className="text-green-600">
            Online
          </span>
        </div>

        <div className="flex justify-between">
          <span>
            Database
          </span>

          <span className="text-green-600">
            Online
          </span>
        </div>

        <div className="flex justify-between">
          <span>
            Authentication
          </span>

          <span className="text-green-600">
            Online
          </span>
        </div>

        <div className="flex justify-between">
          <span>
            Workflow Engine
          </span>

          <span className="text-green-600">
            Online
          </span>
        </div>
      </div>
    </Card>
  );
}