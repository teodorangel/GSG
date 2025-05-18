"use client";
import { useEffect, useState } from "react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const PAGE_SIZE = 10;

async function fetchDocuments(page = 0, limit = PAGE_SIZE) {
  const res = await fetch(`/api/admin/documents?offset=${page * limit}&limit=${limit}`);
  if (!res.ok) return { items: [], total: 0 };
  return await res.json();
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetchDocuments(page, PAGE_SIZE).then((data) => {
      setDocuments(data.items);
      setTotal(data.total);
    });
  }, [page]);

  const hasNext = (page + 1) * PAGE_SIZE < total;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Documents</h1>
      <div className="overflow-x-auto bg-white rounded-lg shadow-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>URL</TableHead>
              <TableHead>Product ID</TableHead>
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
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="flex justify-between mt-6">
        <Button
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
          title="Go to previous page"
        >
          Prev
        </Button>
        <Button
          disabled={!hasNext}
          onClick={() => setPage(page + 1)}
          title="Go to next page"
        >
          Next
        </Button>
      </div>
    </div>
  );
} 