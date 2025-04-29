import { useQuery } from '@tanstack/react-query';

export interface ProductItem {
  id: number;
  model: string;
  name?: string;
  category?: string;
  price?: number;
  brand?: string;
  created_at: string;
}

export interface ProductListOut {
  items: ProductItem[];
  total: number;
}

async function fetchProducts(skip: number, limit: number): Promise<ProductListOut> {
  const res = await fetch(`/products?skip=${skip}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export function useProducts(skip: number, limit: number) {
  return useQuery(['products', skip, limit], () => fetchProducts(skip, limit));
}
