import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-50 to-purple-50 p-6">
      <div className="w-full max-w-4xl space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 text-center">Dashboard</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Link
            href="/crawl"
            className="block p-6 bg-white rounded-lg shadow hover:bg-gray-100 transition"
          >
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Crawl Jobs &rarr;</h2>
            <p className="text-gray-600">Start and monitor web crawls.</p>
          </Link>
          <Link
            href="/products"
            className="block p-6 bg-white rounded-lg shadow hover:bg-gray-100 transition"
          >
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Products &rarr;</h2>
            <p className="text-gray-600">Browse extracted products.</p>
          </Link>
          <Link
            href="/qa"
            className="block p-6 bg-white rounded-lg shadow hover:bg-gray-100 transition"
          >
            <h2 className="text-xl font-semibold text-gray-800 mb-2">QA &rarr;</h2>
            <p className="text-gray-600">Ask questions about products.</p>
          </Link>
          <Link
            href="/plan"
            className="block p-6 bg-white rounded-lg shadow hover:bg-gray-100 transition"
          >
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Planner &rarr;</h2>
            <p className="text-gray-600">Generate project plans and BOMs.</p>
          </Link>
        </div>
      </div>
    </div>
  );
} 