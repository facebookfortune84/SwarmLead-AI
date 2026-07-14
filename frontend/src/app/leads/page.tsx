"use client";

import {
  useMemo,
  useState,
} from "react";

import { AppShell } from "@/components/layout/app-shell";

import { LeadTable } from "@/components/leads/lead-table";
import { LeadSearch } from "@/components/leads/lead-search";
import { LeadCreateDialog } from "@/components/leads/lead-create-dialog";
import { LeadDetailSheet } from "@/components/leads/lead-detail-sheet";

import { useLeads } from "@/hooks/use-leads";

import { Lead } from "@/types/lead";

export default function LeadsPage() {
  const [search, setSearch] =
    useState("");

  const [
    selectedLead,
    setSelectedLead,
  ] =
    useState<Lead | null>(
      null
    );

  const {
    data = [],
    isLoading,
  } = useLeads();

  const leads = useMemo(() => {
    const query =
      search.toLowerCase();

    return data.filter(
      (lead) =>
        lead.email
          .toLowerCase()
          .includes(query) ||
        (lead.name ?? "")
          .toLowerCase()
          .includes(query) ||
        (lead.company ?? "")
          .toLowerCase()
          .includes(query)
    );
  }, [data, search]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              Leads
            </h1>

            <p className="text-muted-foreground">
              Manage lead records
              and outreach
              targets.
            </p>
          </div>

          <LeadCreateDialog />
        </div>

        <LeadSearch
          value={search}
          onChange={setSearch}
        />

        {isLoading ? (
          <div>
            Loading leads...
          </div>
        ) : (
          <LeadTable
            leads={leads}
            onSelect={
              setSelectedLead
            }
          />
        )}

        <LeadDetailSheet
          lead={selectedLead}
          open={!!selectedLead}
          onOpenChange={() =>
            setSelectedLead(null)
          }
        />
      </div>
    </AppShell>
  );
}