import { useMutation } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';

interface StopResponse {
  job_id: string;
  status: string;
}

async function stopCrawl(jobId: string): Promise<StopResponse> {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
  const res = await fetch(`${apiBase}/logs/stop/${jobId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to stop crawl');
  return res.json();
}

export function useStopCrawl(): UseMutationResult<StopResponse, Error, string> {
  return useMutation<StopResponse, Error, string>({
    mutationKey: ['stopCrawl'],
    mutationFn: (jobId: string) => stopCrawl(jobId),
  });
} 