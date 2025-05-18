import { useMutation } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';

export interface CrawlParams {
  domain: string;
  depth?: number;
  concurrency?: number;
  delay?: number;
  use_proxies?: boolean;
  limit?: number;
}

interface CrawlResponse {
  job_id: string;
  status: string;
}

async function startCrawl(params: CrawlParams): Promise<CrawlResponse> {
  // Determine API base URL (NEXT_PUBLIC_API_URL or localhost:8000)
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
  console.log(`🛫 startCrawl calling: ${apiBase}/crawl`, params);
  const res = await fetch(`${apiBase}/crawl/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to start crawl');
  return res.json();
}

// Define mutation hook return type
export function useStartCrawl(): UseMutationResult<CrawlResponse, Error, CrawlParams> {
  // Use the options-based overload to specify only the mutationFn
  return useMutation<CrawlResponse, Error, CrawlParams>({
    mutationKey: ['startCrawl'],
    mutationFn: (params: CrawlParams) => startCrawl(params),
  });
}