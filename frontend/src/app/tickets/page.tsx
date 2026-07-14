"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function TicketsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Ticket Center
          </h1>

          <p className="text-muted-foreground">
            Customer support, escalations,
            AI handoffs, and future voice transfer.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Open
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              In Progress
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Resolved
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Escalated
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">
                Support Queue
              </h2>

              <p className="text-sm text-muted-foreground">
                Ticket management workspace.
              </p>
            </div>

            <Button>
              Create Ticket
            </Button>
          </div>

          <div className="mt-6 rounded-lg border p-12 text-center">
            <div className="text-lg font-semibold">
              No Tickets
            </div>

            <div className="mt-2 text-muted-foreground">
              Ticket infrastructure has been prepared.
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold">
            Escalation Path
          </h2>

          <div className="mt-4 space-y-3">
            <div className="rounded-lg border p-3">
              Ticket
            </div>

            <div className="rounded-lg border p-3">
              AI Resolution Agent
            </div>

            <div className="rounded-lg border p-3">
              Human Assignment
            </div>

            <div className="rounded-lg border p-3">
              Voice Escalation
            </div>

            <div className="rounded-lg border p-3">
              Barge-In Supervisor
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}