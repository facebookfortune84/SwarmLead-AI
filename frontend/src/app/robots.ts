import type { MetadataRoute } from "next";
import { requestOrigin } from "@/lib/server-site";

export default async function robots(): Promise<MetadataRoute.Robots> {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin/", "/api/"],
    },
    sitemap: `${await requestOrigin()}/sitemap.xml`,
  };
}
