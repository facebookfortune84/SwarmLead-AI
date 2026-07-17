"use client";

import {
  ReactQueryDevtools,
} from "@tanstack/react-query-devtools";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import {
  useState,
} from "react";

interface Props {
  children: React.ReactNode;
}

export function QueryProvider({
  children,
}: Props) {
  const [queryClient] =
    useState(
      () =>
        new QueryClient({
          defaultOptions: {
            queries: {
              retry: 1,

              staleTime:
                60_000,

              refetchOnWindowFocus:
                false,
            },
          },
        })
    );

  return (
    <QueryClientProvider
      client={queryClient}
    >
      {children}

      <ReactQueryDevtools
        initialIsOpen={false}
      />
    </QueryClientProvider>
  );
}