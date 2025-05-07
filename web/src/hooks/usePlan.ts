import { useMutation } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';

export interface PlanRequest {
  product_ids: number[];
  budget?: number;
  site_size_sqft?: number;
}

export interface PlanResponse {
  steps: string[];
  bill_of_materials: Record<string, number>;
  estimates: Record<string, any>;
}

async function fetchPlan(params: PlanRequest): Promise<PlanResponse> {
  const res = await fetch('/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Plan request failed');
  return res.json();
}

export function usePlan(): UseMutationResult<PlanResponse, Error, PlanRequest> {
  return useMutation<PlanResponse, Error, PlanRequest>({
    mutationKey: ['plan'],
    mutationFn: (params: PlanRequest) => fetchPlan(params),
  });
}