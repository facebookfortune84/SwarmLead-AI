import Link from "next/link";

export default function CancelPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-gray-50/30 to-white flex items-center justify-center">
      <div className="text-center px-6 max-w-lg mx-auto">
        <div className="w-16 h-16 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center mx-auto mb-6">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Checkout Cancelled
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Your payment was not processed. No charges were made. You can try
          again whenever you&apos;re ready.
        </p>
        <Link
          href="/billing"
          className="inline-block px-8 py-4 bg-gradient-to-r from-primary-700 to-primary-900 text-white font-semibold rounded-xl hover:from-primary-800 hover:to-primary-900 shadow-lg hover:shadow-xl transition-all duration-300"
        >
          Back to Billing
        </Link>
      </div>
    </main>
  );
}
