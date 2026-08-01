import type { Metadata } from "next";
import Link from "next/link";
import { industries } from "@/lib/industries";

export const metadata: Metadata = {
  title: "Industries — AI Lead Generation by Vertical",
  description:
    "Genesis automates lead generation across 12 industries with a full-duplex voice agent and a 15-agent workforce. See how it works for yours.",
  alternates: { canonical: "/industries" },
};

export default function IndustriesPage() {
  return (
    <main className="min-h-screen bg-[#0a0a1a] text-white">
      <div className="mx-auto max-w-5xl px-6 py-20">
        <nav className="text-sm text-white/40 mb-8">
          <Link href="/" className="hover:text-white/70">
            Home
          </Link>{" "}
          / <span className="text-white/70">Industries</span>
        </nav>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          AI Lead Generation, by Industry
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-white/70">
          Genesis runs a full-duplex voice agent and a 15-agent workforce that
          answers your line in real time, qualifies leads, and automates follow-up.
          Pick your vertical.
        </p>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {industries.map((i) => (
            <Link
              key={i.slug}
              href={`/industries/${i.slug}`}
              className="group rounded-2xl border border-white/10 bg-white/5 p-6 transition hover:border-emerald-500/40 hover:bg-white/10"
            >
              <span className="inline-block rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs uppercase tracking-wider text-white/50">
                {i.name}
              </span>
              <h2 className="mt-3 font-semibold text-white">{i.h1}</h2>
              <p className="mt-2 text-sm text-white/60">{i.description}</p>
              <span className="mt-4 inline-block text-sm font-semibold text-emerald-400">
                Learn more →
              </span>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
