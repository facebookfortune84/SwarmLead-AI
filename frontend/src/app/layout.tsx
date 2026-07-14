import "./globals.css";

import { QueryProvider } from "@/components/providers/query-provider";
import { AppThemeProvider } from "@/components/providers/theme-provider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AppThemeProvider>
          <QueryProvider>
            {children}
          </QueryProvider>
        </AppThemeProvider>
      </body>
    </html>
  );
}