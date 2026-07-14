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

import { Button } from "@/components/ui/button";

import { useLeads } from "@/hooks/use-leads";

import { Lead } from "@/types/lead";

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

  const filteredLeads =
    useMemo(() => {
      const query =
        search.toLowerCase();

      return data
        .filter(
          (lead) =>
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
        .sort((a, b) => {
          if (
            sortBy === "created"
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
        });
    }, [data, search, sortBy]);

  const pageCount =
    Math.ceil(
      filteredLeads.length /
        PAGE_SIZE
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
              Manage lead
              records,
              outreach,
              ownership,
              and agent
              discovery.
            </p>
          </div>

          <LeadCreateDialog />
        </div>

        <div className="flex gap-2">
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
          onChange={(v) => {
            setSearch(v);
            setPage(1);
          }}
        />

        {isLoading ? (
          <div>
            Loading leads...
          </div>
        ) : (
          <>
            <LeadTable
              leads={
                paginatedLeads
              }
              onSelect={
                setSelectedLead
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

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  disabled={
                    page === 1
                  }
                  onClick={() =>
                    setPage(
                      (p) =>
                        p - 1
                    )
                  }
                >
                  Previous
                </Button>

                <div className="flex items-center px-3 text-sm">
                  {page} /{" "}
                  {pageCount || 1}
                </div>

                <Button
                  variant="outline"
                  disabled={
                    page >=
                    pageCount
                  }
                  onClick={() =>
                    setPage(
                      (p) =>
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