import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Business Skeleton Generator — Free AI Tool",
  description:
    "Type a business idea and get a complete launch skeleton — files, infra plan and checklist — in seconds. Free AI tool from Genesis.",
  alternates: { canonical: "/tools/business-skeleton" },
  openGraph: {
    title: "Business Skeleton Generator — Free AI Tool",
    description:
      "Type a business idea and get a complete launch skeleton — files, infra plan and checklist — in seconds.",
    url: "https://realms2riches.com/tools/business-skeleton",
    type: "website",
  },
};

export default function BusinessSkeletonLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
