import { useState } from 'react';
import { useProducts } from '../../hooks/useProducts';

export default function ProductsPage() {
  const [page, setPage] = useState(0);
  const limit = 10;
  const { data, isLoading, error } = useProducts(page * limit, limit);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading products</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Products</h1>
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th>ID</th>
            <th>Model</th>
            <th>Name</th>
            <th>Category</th>
            <th>Price</th>
            <th>Brand</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map((prod) => (
            <tr key={prod.id} className="border-t">
              <td>{prod.id}</td>
              <td>{prod.model}</td>
              <td>{prod.name}</td>
              <td>{prod.category}</td>
              <td>{prod.price}</td>
              <td>{prod.brand}</td>
              <td>{new Date(prod.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
        <button onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
}