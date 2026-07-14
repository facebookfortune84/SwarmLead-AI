"use client";

import { useQuery } from "@tanstack/react-query";

export function useAgents() {
  return useQuery({
    queryKey: ["agents"],

    queryFn: async () => {
      return [
        {
          id: "discovery",
          name:
            "Discovery Agent",
          type:
            "DISCOVERY",
          status: "READY",
        },

        {
          id: "qualification",
          name:
            "Qualification Agent",
          type:
            "QUALIFICATION",
          status: "READY",
        },

        {
          id: "outreach",
          name:
            "Outreach Agent",
          type:
            "OUTREACH",
          status: "READY",
        },

        {
          id: "voice",
          name:
            "Voice Agent",
          type: "VOICE",
          status: "PLANNED",
        },
      ];
    },
  });
}