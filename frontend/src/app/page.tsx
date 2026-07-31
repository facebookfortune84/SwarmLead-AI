import Image from "next/image";
import Link from "next/link";
import { FeatureShowcase, SocialProof, CTASection, Testimonials } from "@/components/landing/FeatureShowcase";
import { VoiceLandingAgent } from "@/components/landing/VoiceLandingAgent";

export default function Home() {
  return (
    <main className="min-h-screen" id="main-content">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-gray-900 focus:rounded-lg focus:shadow-lg">
        Skip to content
      </a>
      <Header />
      <HeroSection />
      <FeatureShowcase />
      <PricingShowcase />
      <Testimonials />
      <SocialProof />
      <CTASection />
      <VoiceLandingAgent />
    </main>
  );
}

function Header() {
  return (
    <header className="relative z-20 px-6 py-4">
      <nav className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <Image
            src="/genesis_forge_logo_1.png"
            alt="Genesis Forge"
            width={32}
            height={32}
            className="rounded-lg group-hover:scale-110 transition-transform"
          />
          <span className="text-white font-bold text-lg">Genesis Forge</span>
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/demo" className="text-white/60 hover:text-white/80 transition-colors text-sm font-medium">Demo</Link>
          <Link href="/login" className="text-white/60 hover:text-white/80 transition-colors text-sm font-medium">Sign In</Link>
          <Link href="/onboarding" className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold rounded-lg hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all">
            Get Started
          </Link>
        </div>
      </nav>
    </header>
  );
}

function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-950 via-indigo-950/90 to-gray-950">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-violet-500/15 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-600/5 via-transparent to-transparent" />

      <div className="absolute inset-0 opacity-10">
        <Image
          src="/genesis_forge_hero_image_1.png"
          alt=""
          fill
          className="object-cover"
          priority
          aria-hidden="true"
        />
      </div>

      <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
        <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full text-sm font-medium text-white/80">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
          Voice AI is live — start a conversation
        </div>

        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white mb-6 tracking-tight leading-tight">
          Launch your business
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            with your voice
          </span>
        </h1>

        <p className="text-lg md:text-xl text-white/60 mb-10 max-w-2xl mx-auto leading-relaxed">
          Genesis is the first autonomous business launch platform powered by constitutional voice AI.
          Speak your vision — we handle the rest. From lead generation to workflow automation.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/onboarding"
            className="group relative px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all duration-300 text-lg overflow-hidden"
          >
            <span className="relative z-10">Get Started — No Credit Card</span>
            <div className="absolute inset-0 -translate-x-full group-hover:translate-x-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700" />
          </Link>
          <Link
            href="/demo"
            className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 hover:border-white/20 shadow-sm hover:shadow-md transition-all duration-300 text-lg"
          >
            View Demo
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
          {[
            { value: "10x", label: "Faster Launch" },
            { value: "85%", label: "Lead Conversion" },
            { value: "3min", label: "Avg Setup" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-white">{stat.value}</div>
              <div className="text-sm text-white/50 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PricingShowcase() {
  const plans = [
    {
      name: "Starter",
      price: "$29",
      image: "/stripe_image_genesis_starter.png",
      features: ["CRM", "Lead Management", "Workflow Engine", "Single Tenant", "Basic Outreach"],
    },
    {
      name: "Growth",
      price: "$99",
      image: "/stripe_image_genesis_growth.png",
      features: ["Everything in Starter", "Advanced Workflows", "Multi-Tenant", "Campaign Outreach", "Reporting"],
    },
    {
      name: "Enterprise",
      price: "$299",
      image: "/stripe_image_genesis_enterprise.png",
      features: ["Everything in Growth", "Unlimited Tenants", "Voice Runtime", "Agent Runtime", "Priority Support"],
    },
  ];

  return (
    <section className="py-20 px-6 bg-gradient-to-b from-transparent via-indigo-950/30 to-transparent">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Choose Your{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Launch Plan
            </span>
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            Start free, upgrade as you grow. No hidden fees, no surprises.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <div
              key={plan.name}
              className="group relative bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-8 hover:border-indigo-500/30 transition-all duration-300 overflow-hidden"
            >
              {i === 1 && (
                <div className="absolute top-0 right-0 px-3 py-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold rounded-bl-xl">
                  Most Popular
                </div>
              )}
              <div className="relative h-40 mb-6 rounded-xl overflow-hidden bg-white/5">
                <Image
                  src={plan.image}
                  alt={`${plan.name} plan`}
                  fill
                  className="object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <h3 className="text-2xl font-bold text-white">{plan.name}</h3>
              <div className="mt-2 text-4xl font-bold text-white">
                {plan.price}
                <span className="text-lg text-white/50">/mo</span>
              </div>
              <ul className="mt-6 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-white/70">
                    <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/onboarding"
                className="mt-8 block w-full text-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
              >
                Get Started
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}