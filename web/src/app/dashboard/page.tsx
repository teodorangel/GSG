import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default function DashboardPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-50 to-purple-50 p-6">
      <div className="w-full max-w-4xl space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 text-center">Dashboard</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Link href="/crawl" passHref>
            <Card className="hover:bg-gray-100 transition">
              <CardHeader>
                <CardTitle>Crawl Jobs &rarr;</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Start and monitor web crawls.</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/products" passHref>
            <Card className="hover:bg-gray-100 transition">
              <CardHeader>
                <CardTitle>Products &rarr;</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Browse extracted products.</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/qa" passHref>
            <Card className="hover:bg-gray-100 transition">
              <CardHeader>
                <CardTitle>QA &rarr;</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Ask questions about products.</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/plan" passHref>
            <Card className="hover:bg-gray-100 transition">
              <CardHeader>
                <CardTitle>Planner &rarr;</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Generate project plans and BOMs.</p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
} 