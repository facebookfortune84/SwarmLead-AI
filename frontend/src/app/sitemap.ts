import type { MetadataRoute } from "next";
import { industries } from "@/lib/industries";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.SITE_URL || "https://realms2riches.com";
  const today = new Date();

  const staticPages = [
    { url: baseUrl, changeFrequency: "weekly" as const, priority: 1 },
    { url: `${baseUrl}/industries`, changeFrequency: "weekly" as const, priority: 0.9 },
    { url: `${baseUrl}/tools/business-skeleton`, changeFrequency: "weekly" as const, priority: 0.8 },
    { url: `${baseUrl}/onboarding`, changeFrequency: "monthly" as const, priority: 0.7 },
    { url: `${baseUrl}/demo`, changeFrequency: "monthly" as const, priority: 0.7 },
  ];

  const industryPages = industries.map((i) => ({
    url: `${baseUrl}/industries/${i.slug}`,
    lastModified: today,
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));

  return [...staticPages, ...industryPages];
}
