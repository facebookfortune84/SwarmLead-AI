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
import { LeadMetrics } from "@/components/leads/lead-metrics";

import { Button } from "@/components/ui/button";

import { useLeads } from "@/hooks/use-leads";

import {
  Lead,
} from "@/types/lead";

const PAGE_SIZE = 15;

export default function LeadsPage() {
  const [search, setSearch] =
    useState("");

  const [sortBy, setSortBy] =
    useState<
      "created" | "name"
    >("created");

  const [page, setPage] =
    useState(1);

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

  const leads =
    data as Lead[];

  const filteredLeads =
    useMemo(() => {
      const query =
        search.toLowerCase();

      return leads
        .filter(
          (lead: Lead) =>
            lead.email
              .toLowerCase()
              .includes(query) ||
            (
              lead.name ?? ""
            )
              .toLowerCase()
              .includes(query) ||
            (
              lead.company ?? ""
            )
              .toLowerCase()
              .includes(query)
        )
        .sort(
          (
            a: Lead,
            b: Lead
          ) => {
            if (
              sortBy ===
              "created"
            ) {
              return (
                new Date(
                  b.created_at
                ).getTime() -
                new Date(
                  a.created_at
                ).getTime()
              );
            }

            return (
              a.name ?? ""
            ).localeCompare(
              b.name ?? ""
            );
          }
        );
    }, [
      leads,
      search,
      sortBy,
    ]);

  const pageCount =
    Math.max(
      1,
      Math.ceil(
        filteredLeads.length /
          PAGE_SIZE
      )
    );

  const paginatedLeads =
    filteredLeads.slice(
      (page - 1) *
        PAGE_SIZE,
      page * PAGE_SIZE
    );

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              Leads
            </h1>

            <p className="text-muted-foreground">
              Manage lead discovery,
              qualification,
              outreach,
              ownership,
              and future AI agent activity.
            </p>
          </div>

          <LeadCreateDialog />
        </div>

        <LeadMetrics
          leads={filteredLeads}
        />

        <div className="flex flex-wrap gap-2">
          <Button
            variant={
              sortBy ===
              "created"
                ? "default"
                : "outline"
            }
            onClick={() =>
              setSortBy(
                "created"
              )
            }
          >
            Newest
          </Button>

          <Button
            variant={
              sortBy === "name"
                ? "default"
                : "outline"
            }
            onClick={() =>
              setSortBy(
                "name"
              )
            }
          >
            Name
          </Button>
        </div>

        <LeadSearch
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(1);
          }}
        />

        {isLoading ? (
          <div className="rounded-xl border p-8 text-center">
            Loading leads...
          </div>
        ) : filteredLeads.length ===
          0 ? (
          <div className="rounded-xl border p-8 text-center">
            <div className="text-lg font-semibold">
              No leads found
            </div>

            <div className="mt-1 text-sm text-muted-foreground">
              Try adjusting your
              search or create a
              new lead.
            </div>
          </div>
        ) : (
          <>
            <LeadTable
              leads={
                paginatedLeads
              }
            />

            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing{" "}
                {
                  paginatedLeads.length
                }{" "}
                of{" "}
                {
                  filteredLeads.length
                }{" "}
                leads
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  disabled={
                    page === 1
                  }
                  onClick={() =>
                    setPage(
                      (
                        p
                      ) =>
                        p - 1
                    )
                  }
                >
                  Previous
                </Button>

                <div className="px-3 text-sm">
                  Page {page} of{" "}
                  {pageCount}
                </div>

                <Button
                  variant="outline"
                  disabled={
                    page >=
                    pageCount
                  }
                  onClick={() =>
                    setPage(
                      (
                        p
                      ) =>
                        p + 1
                    )
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        )}

        <LeadDetailSheet
          lead={selectedLead}
          open={
            !!selectedLead
          }
          onOpenChange={() =>
            setSelectedLead(
              null
            )
          }
        />
      </div>
    </AppShell>
  );
}