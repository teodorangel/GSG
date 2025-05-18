"use client";
import React, { useState, useMemo } from 'react';
import { useProducts } from '../../hooks/useProducts';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table';

function DatabasePage() {
  const [page, setPage] = useState(0);
  const limit = 20;
  const { data, isLoading, error } = useProducts(page * limit, limit);
  const items = data?.items ?? [];
  const hasNext = data ? (page + 1) * limit < data.total : false;

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading data: {error.message}</div>;
  if (items.length === 0) return <div>No data found</div>;

  return (
    <div className="p-6 bg-gray-50 text-gray-900 min-h-screen">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Database: Scraped Products</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-2">This table shows the raw scraped product data from the database.</p>
        </CardContent>
      </Card>
      <div className="overflow-x-auto bg-white rounded-lg shadow-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Brand</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Images</TableHead>
              <TableHead>Documents</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            { items.map((prod) => (
              <TableRow key={prod.id} className="hover:bg-gray-50">
                <TableCell>{prod.id}</TableCell>
                <TableCell>{prod.model}</TableCell>
                <TableCell>{prod.name}</TableCell>
                <TableCell>{prod.category}</TableCell>
                <TableCell>{prod.price}</TableCell>
                <TableCell>{prod.brand}</TableCell>
                <TableCell>{new Date(prod.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  <div className="flex space-x-2">
                    {prod.images.map((url) => (
                      <img
                        key={url}
                        src={url}
                        alt="product"
                        className="h-10 w-10 object-cover rounded"
                      />
                    ))}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="space-x-2">
                    {prod.documents.map((url) => (
                      <a
                        key={url}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {new URL(url).pathname.split('/').pop()}
                      </a>
                    ))}
                  </div>
                </TableCell>
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

export default DatabasePage; 