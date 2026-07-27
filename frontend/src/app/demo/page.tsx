import Link from "next/link";

export default function DemoPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-primary-50/30 to-white">
      <div className="mx-auto max-w-4xl px-6 py-24 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          See Genesis in Action
        </h1>
        <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
          Watch how Genesis uses constitutional voice AI to launch, manage, and
          grow your business — all from a single conversation.
        </p>

        <div className="aspect-video bg-gray-100 rounded-2xl border border-gray-200 flex items-center justify-center mb-12" role="img" aria-label="Demo video placeholder">
          <p className="text-gray-400 text-lg">
            Demo video placeholder
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left mb-12">
          {[
            {
              step: "1",
              title: "Voice Discovery",
              description: "Tell Genesis about your business idea using natural voice conversation.",
            },
            {
              step: "2",
              title: "AI-Powered Setup",
              description: "Genesis automatically configures your CRM, workflows, and outreach.",
            },
            {
              step: "3",
              title: "Launch & Monitor",
              description: "Go live and track performance from your dashboard.",
            },
          ].map((item) => (
            <div key={item.step} className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="w-10 h-10 rounded-full bg-primary-700 text-white flex items-center justify-center font-bold mb-4" aria-hidden="true">
                {item.step}
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
              <p className="text-sm text-gray-600">{item.description}</p>
            </div>
          ))}
        </div>

        <Link
          href="/onboarding"
          className="inline-block px-8 py-4 bg-gradient-to-r from-primary-700 to-primary-900 text-white font-semibold rounded-xl hover:from-primary-800 hover:to-primary-900 shadow-lg hover:shadow-xl transition-all duration-300 text-lg"
        >
          Start Free — No Credit Card
        </Link>
      </div>
    </main>
  );
}
