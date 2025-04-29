import { useMutation } from '@tanstack/react-query';

export interface CrawlParams {
  domain: string;
  depth?: number;
  concurrency?: number;
  delay?: number;
}

interface CrawlResponse {
  job_id: string;
  status: string;
}

async function startCrawl(params: CrawlParams): Promise<CrawlResponse> {
  const res = await fetch('/crawl', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to start crawl');
  return res.json();
}

export function useStartCrawl() {
  return useMutation((params: CrawlParams) => startCrawl(params));
}