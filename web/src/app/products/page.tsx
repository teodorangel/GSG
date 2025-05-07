"use client";
import { useState, useMemo } from 'react';
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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function ProductsPage() {
  const [page, setPage] = useState(0);
  const limit = 10;
  const { data, isLoading, error } = useProducts(page * limit, limit);
  const items = data?.items ?? [];
  const hasNext = data ? (page + 1) * limit < data.total : false;
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
    const total = data?.total ?? 0;
    const prices = items.map(p => p.price || 0);
    const avgPrice = total > 0 ? (prices.reduce((a,b)=>a+b,0)/items.length).toFixed(2) : '0.00';
    // Category counts
    const counts: Record<string, number> = {};
    items.forEach(p => {
      const cat = p.category || 'Uncategorized';
      counts[cat] = (counts[cat] || 0) + 1;
    });
    const categories = Object.keys(counts);
    const values = categories.map(c => counts[c]);
    return { total, avgPrice, categories, values };
  }, [data, items]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading products: {error.message}</div>;
  if (items.length === 0) return <div>No products found</div>;

  return (
    <div className="p-6 bg-gray-50 text-gray-900 min-h-screen">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-4xl font-extrabold text-gray-800">Products</h1>
        <button
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-800 disabled:bg-gray-300 transition-colors duration-200 shadow hover:shadow-md"
          onClick={() => cleanupMutation.mutate()}
          disabled={cleanupMutation.status === 'pending'}
          title="Remove duplicate images for all products"
        >
          Cleanup Duplicates
        </button>
      </div>
      {cleanupMsg && (
        <div className="mb-4 p-2 bg-blue-100 text-blue-800 rounded shadow inline-block">{cleanupMsg}</div>
      )}
      <h1 className="text-3xl font-bold mb-6">Products</h1>
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl">Total Products</h2>
          <p className="text-2xl font-semibold">{stats.total}</p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl">Average Price</h2>
          <p className="text-2xl font-semibold text-indigo-600">${stats.avgPrice}</p>
        </div>
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
        <table className="min-w-full bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Model</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Category</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Price</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Brand</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Created At</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Images</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Documents</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            { items.map((prod) => (
              <tr key={prod.id} className="hover:bg-gray-50">
                <td className="px-4 py-2">{prod.id}</td>
                <td className="px-4 py-2">{prod.model}</td>
                <td className="px-4 py-2">{prod.name}</td>
                <td className="px-4 py-2">{prod.category}</td>
                <td className="px-4 py-2">{prod.price}</td>
                <td className="px-4 py-2">{prod.brand}</td>
                <td className="px-4 py-2">{new Date(prod.created_at).toLocaleString()}</td>
                <td className="px-4 py-2 flex space-x-2">
                  {prod.images.map((url) => (
                    <img
                      key={url}
                      src={url}
                      alt="product"
                      className="h-10 w-10 object-cover rounded transform transition-transform duration-200 hover:scale-110"
                    />
                  ))}
                </td>
                <td className="px-4 py-2 space-x-2">
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
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex justify-between mt-6">
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-800 disabled:bg-gray-300 transition-colors duration-200 shadow hover:shadow-md"
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
          title="Go to previous page"
        >
          Prev
        </button>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-800 disabled:bg-gray-300 transition-colors duration-200 shadow hover:shadow-md"
          disabled={!hasNext}
          onClick={() => setPage(page + 1)}
          title="Go to next page"
        >
          Next
        </button>
      </div>
    </div>
  );
}