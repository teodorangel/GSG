import { useQuery, type UseQueryResult } from '@tanstack/react-query';

export interface ProductItem {
  id: number;
  model: string;
  name?: string;
  category?: string;
  price?: number;
  brand?: string;
  created_at: string;
  images: string[];
  documents: string[];
}

export interface ProductListOut {
  items: ProductItem[];
  total: number;
}

// Determine API base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function fetchProducts(skip: number, limit: number): Promise<ProductListOut> {
  const url = `${API_BASE}/products/?skip=${skip}&limit=${limit}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export function useProducts(skip: number, limit: number): UseQueryResult<ProductListOut, Error> {
  return useQuery<ProductListOut, Error>({
    queryKey: ['products', skip, limit],
    queryFn: () => fetchProducts(skip, limit),
  });
}
