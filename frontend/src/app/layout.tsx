import "./globals.css";

import { AppThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <AppThemeProvider>
          <QueryProvider>
            {children}
          </QueryProvider>
        </AppThemeProvider>
      </body>
    </html>
  );
}
