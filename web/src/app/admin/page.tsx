"use client";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function AdminPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-gray-50 to-blue-50 p-6">
      <div className="w-full max-w-2xl space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 text-center mb-6">Admin Dashboard</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Link href="/admin/products" passHref>
            <Card className="hover:bg-gray-100 transition cursor-pointer">
              <CardHeader>
                <CardTitle>Manage Products</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">View, edit, and delete products.</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/admin/documents" passHref>
            <Card className="hover:bg-gray-100 transition cursor-pointer">
              <CardHeader>
                <CardTitle>Manage Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">View and manage product documents (PDFs).</p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
} 