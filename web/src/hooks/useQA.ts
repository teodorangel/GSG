import { useMutation, type UseMutationResult } from '@tanstack/react-query';

export interface QARequest { query: string; product_id?: number; }
export interface QAResponse { answer: string; sources: string[]; }

async function fetchQA(params: QARequest): Promise<QAResponse> {
  const res = await fetch('/qa', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('QA request failed');
  return res.json();
}

export function useQA(): UseMutationResult<QAResponse, Error, QARequest> {
  return useMutation<QAResponse, Error, QARequest>({
    mutationKey: ['qa'],
    mutationFn: (params: QARequest) => fetchQA(params),
  });
}
