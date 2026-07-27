import Link from "next/link";

export default function SuccessPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-green-50/30 to-white flex items-center justify-center">
      <div className="text-center px-6 max-w-lg mx-auto">
        <div className="w-16 h-16 rounded-full bg-green-100 text-green-700 flex items-center justify-center mx-auto mb-6">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Payment Successful!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Thank you for your subscription. Your account is now active and you
          can start using all Genesis features.
        </p>
        <Link
          href="/dashboard"
          className="inline-block px-8 py-4 bg-gradient-to-r from-primary-700 to-primary-900 text-white font-semibold rounded-xl hover:from-primary-800 hover:to-primary-900 shadow-lg hover:shadow-xl transition-all duration-300"
        >
          Go to Dashboard
        </Link>
      </div>
    </main>
  );
}
