"use client";
import { useEffect, useState } from "react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const PAGE_SIZE = 10;

async function fetchProducts(page = 0, limit = PAGE_SIZE) {
  const res = await fetch(`/api/admin/products?offset=${page * limit}&limit=${limit}`);
  if (!res.ok) return { items: [], total: 0 };
  return await res.json();
}

export default function AdminProductsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetchProducts(page, PAGE_SIZE).then((data) => {
      setProducts(data.items);
      setTotal(data.total);
    });
  }, [page]);

  const hasNext = (page + 1) * PAGE_SIZE < total;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Manage Products</h1>
      <div className="mb-4">
        <a
          href="/static/images"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="secondary">Open Images Directory</Button>
        </a>
      </div>
      <div className="overflow-x-auto bg-white rounded-lg shadow-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Image</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Brand</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {products.map((prod) => (
              <TableRow key={prod.id}>
                <TableCell>{prod.id}</TableCell>
                <TableCell>
                  {prod.images && prod.images.length > 0 ? (
                    <img
                      src={prod.images[0]}
                      alt={prod.name || prod.model}
                      style={{ width: 64, height: 64, objectFit: "cover", borderRadius: 8 }}
                    />
                  ) : (
                    <span className="text-gray-400">No image</span>
                  )}
                </TableCell>
                <TableCell>{prod.model}</TableCell>
                <TableCell>{prod.name}</TableCell>
                <TableCell>{prod.category}</TableCell>
                <TableCell>{prod.price}</TableCell>
                <TableCell>{prod.brand}</TableCell>
                <TableCell>
                  <Button size="sm" variant="outline" className="mr-2">Edit</Button>
                  <Button size="sm" variant="destructive">Delete</Button>
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