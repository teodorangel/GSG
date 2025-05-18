"use client";
import { useEffect, useState } from "react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

// Placeholder fetch function (replace with real API call)
async function fetchDocuments() {
  const res = await fetch("/api/admin/documents");
  if (!res.ok) return { items: [], total: 0 };
  return res.json();
}

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  useEffect(() => {
    fetchDocuments().then((data) => setDocuments(data.items || []));
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Manage Documents</h1>
      <div className="mb-4">
        <a
          href="/static/documents"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="secondary">Open Documents Directory</Button>
        </a>
      </div>
      <div className="overflow-x-auto bg-white rounded-lg shadow-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>URL</TableHead>
              <TableHead>Product ID</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell>{doc.id}</TableCell>
                <TableCell>
                  <a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    {doc.url}
                  </a>
                </TableCell>
                <TableCell>{doc.product_id}</TableCell>
                <TableCell>
                  <Button size="sm" variant="outline" className="mr-2">Edit</Button>
                  <Button size="sm" variant="destructive">Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
} 