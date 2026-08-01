import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { industries, industryBySlug } from "@/lib/industries";

type Props = {
  params: Promise<{ slug: string }>;
};

export function generateStaticParams() {
  return industries.map((i) => ({ slug: i.slug }));
}

export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const industry = industryBySlug(slug);
  if (!industry) return {};
  return {
    title: industry.title,
    description: industry.description,
    keywords: industry.keywords,
    alternates: { canonical: `/industries/${industry.slug}` },
    openGraph: {
      title: industry.title,
      description: industry.description,
      type: "website",
      url: `/industries/${industry.slug}`,
    },
  };
}

export default async function IndustryPage({ params }: Props) {
  const { slug } = await params;
  const industry = industryBySlug(slug);
  if (!industry) return notFound();

  return (
    <main className="min-h-screen bg-[#0a0a1a] text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Service",
            name: `Genesis — ${industry.name} Lead Generation`,
            serviceType: "AI lead generation",
            provider: { "@type": "Organization", name: "Genesis" },
            description: industry.description,
            areaServed: "US",
            offers: {
              "@type": "Offer",
              name: "Growth",
              price: "99",
              priceCurrency: "USD",
            },
          }),
        }}
      />
      <div className="mx-auto max-w-4xl px-6 py-20">
        <nav className="text-sm text-white/40 mb-8">
          <Link href="/" className="hover:text-white/70">
            Home
          </Link>{" "}
          /{" "}
          <Link href="/industries" className="hover:text-white/70">
            Industries
          </Link>{" "}
          / <span className="text-white/70">{industry.name}</span>
        </nav>
        <span className="inline-block rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs uppercase tracking-wider text-white/50">
          {industry.name}
        </span>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          {industry.h1}
        </h1>
        <p className="mt-6 text-lg leading-relaxed text-white/70">{industry.body}</p>

        <h2 className="mt-12 text-2xl font-semibold">
          What Genesis fixes for {industry.name}
        </h2>
        <ul className="mt-6 grid gap-3 sm:grid-cols-2">
          {industry.painPoints.map((p) => (
            <li
              key={p}
              className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-white/80"
            >
              {p}
            </li>
          ))}
        </ul>

        <div className="mt-12 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-6">
          <p className="text-lg text-emerald-200">{industry.outcome}</p>
        </div>

        <div className="mt-12 flex flex-wrap gap-2">
          {industry.keywords.map((k) => (
            <span
              key={k}
              className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/50"
            >
              {k}
            </span>
          ))}
        </div>

        <div className="mt-12 rounded-2xl border border-white/10 bg-white/5 p-6 text-center">
          <p className="font-semibold text-white">
            Ready to automate {industry.name} lead generation?
          </p>
          <p className="mt-2 text-sm text-white/60">
            Try the live voice agent on the homepage — it answers in seconds.
          </p>
          <Link
            href="/"
            className="mt-5 inline-block rounded-lg bg-emerald-500 px-6 py-3 text-sm font-semibold text-black transition hover:bg-emerald-400"
          >
            Try Genesis Live
          </Link>
        </div>

        <section className="mt-12 border-t border-white/10 pt-8">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-white/40">
            More industries
          </h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {industries
              .filter((i) => i.slug !== industry.slug)
              .map((i) => (
                <Link
                  key={i.slug}
                  href={`/industries/${i.slug}`}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/60 transition hover:bg-white/10"
                >
                  {i.name}
                </Link>
              ))}
          </div>
        </section>
      </div>
    </main>
  );
}
