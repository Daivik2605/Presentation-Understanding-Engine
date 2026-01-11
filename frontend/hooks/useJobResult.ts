'use client';

import { useQuery } from '@tanstack/react-query';
import { getJobResult, JobResult } from '@/lib/api';

interface UseJobResultReturn {
  result: JobResult | null;
  isLoading: boolean;
  error: string | null;
}

export function useJobResult(jobId: string): UseJobResultReturn {
  const { data, isLoading, error } = useQuery({
    queryKey: ['jobResult', jobId],
    queryFn: () => getJobResult(jobId),
    enabled: !!jobId,
    retry: 3,
  });

  return {
    result: data || null,
    isLoading,
    error: error ? (error as Error).message : null,
  };
}
