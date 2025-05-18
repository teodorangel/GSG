"use client";
import { useState, useMemo, useEffect } from 'react';
import { useProducts } from '../../hooks/useProducts';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useMutation } from '@tanstack/react-query';
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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const PAGE_SIZE = 10;

async function fetchProducts(page = 0, limit = PAGE_SIZE) {
  const res = await fetch(`/products?offset=${page * limit}&limit=${limit}`);
  if (!res.ok) return { items: [], total: 0 };
  return await res.json();
}

export default function ProductsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [cleanupMsg, setCleanupMsg] = useState<string | null>(null);
  const cleanupMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/products/cleanup`, { method: 'POST' });
      if (!res.ok) throw new Error('Cleanup failed');
      return res.json();
    },
    onSuccess: (data) => {
      setCleanupMsg(`Removed ${data.removed} duplicates.`);
      setTimeout(() => setCleanupMsg(null), 3000);
    },
    onError: () => {
      setCleanupMsg('Cleanup failed');
      setTimeout(() => setCleanupMsg(null), 3000);
    }
  });

  // Compute statistics (always run to preserve hook order)
  const stats = useMemo(() => {
    const total = products.length;
    const prices = products.map(p => p.price || 0);
    const avgPrice = total > 0 ? (prices.reduce((a,b)=>a+b,0)/products.length).toFixed(2) : '0.00';
    // Category counts
    const counts: Record<string, number> = {};
    products.forEach(p => {
      const cat = p.category || 'Uncategorized';
      counts[cat] = (counts[cat] || 0) + 1;
    });
    const categories = Object.keys(counts);
    const values = categories.map(c => counts[c]);
    return { total, avgPrice, categories, values };
  }, [products]);

  useEffect(() => {
    fetchProducts(page, PAGE_SIZE).then((data) => {
      setProducts(data.items);
      setTotal(data.total);
    });
  }, [page]);

  const hasNext = (page + 1) * PAGE_SIZE < total;

  return (
    <div className="p-6 bg-gray-50 text-gray-900 min-h-screen">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-4xl font-extrabold text-gray-800">Products</h1>
        <Button
          onClick={() => cleanupMutation.mutate()}
          disabled={cleanupMutation.status === 'pending'}
          title="Remove duplicate images for all products"
        >
          Cleanup Duplicates
        </Button>
      </div>
      {cleanupMsg && (
        <div className="mb-4 p-2 bg-blue-100 text-blue-800 rounded shadow inline-block">{cleanupMsg}</div>
      )}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Products</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">{stats.total}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Average Price</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold text-indigo-600">${stats.avgPrice}</p>
          </CardContent>
        </Card>
      </div>
      <div className="mb-8 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl mb-2">Products by Category</h2>
        <Bar
          data={{
            labels: stats.categories,
            datasets: [{
              label: '# of Items',
              data: stats.values,
              backgroundColor: 'rgba(54, 162, 235, 0.6)',
            }]
          }}
          options={{
            responsive: true,
            plugins: { legend: { position: 'top' }, title: { display: false } }
          }}
        />
      </div>
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
            {products.map((prod) => (
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
                        className="h-10 w-10 object-cover rounded transform transition-transform duration-200 hover:scale-110"
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
                        className="text-blue-600 hover:text-blue-800 hover:underline transition-colors duration-200"
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