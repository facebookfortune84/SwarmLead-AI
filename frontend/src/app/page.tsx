import { FeatureShowcase, SocialProof, CTASection } from "@/components/landing/FeatureShowcase";
import { VoiceLandingAgent, VoiceGreeting } from "@/components/landing/VoiceLandingAgent";

export default function Home() {
  return (
    <main className="min-h-screen" id="main-content">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-gray-900 focus:rounded-lg focus:shadow-lg">
        Skip to content
      </a>
      <HeroSection />
      <FeatureShowcase />
      <SocialProof />
      <CTASection />
      <VoiceLandingAgent />
    </main>
  );
}

function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-white via-primary-50/30 to-white">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary-100/40 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-gold-100/30 via-transparent to-transparent" />
      
      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-full text-sm font-medium text-primary-700">
          <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" aria-hidden="true" />
          Voice AI is live — start a conversation
        </div>

        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-gray-900 mb-6 tracking-tight">
          Launch your business
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-primary-800">
            with your voice
          </span>
        </h1>

        <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
          Genesis is the first autonomous business launch platform powered by constitutional voice AI. 
          Speak your vision — we handle the rest.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <a
            href="/onboarding"
            className="px-8 py-4 bg-gradient-to-r from-primary-700 to-primary-900 text-white font-semibold rounded-xl hover:from-primary-800 hover:to-primary-900 shadow-lg hover:shadow-xl transition-all duration-300 text-lg"
          >
            Start Free — No Credit Card
          </a>
          <a
            href="/demo"
            className="px-8 py-4 bg-white/80 backdrop-blur-sm border border-gray-200 text-gray-900 font-semibold rounded-xl hover:bg-white hover:border-gray-300 shadow-sm hover:shadow-md transition-all duration-300 text-lg"
          >
            Watch Demo
          </a>
        </div>

        <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
          {[
            { value: "10x", label: "Faster Launch" },
            { value: "85%", label: "Lead Conversion" },
            { value: "3min", label: "Avg Setup" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
