import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { Test } from '@/types';

export function useDashboardSummary() {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: () => apiClient.getDashboardSummary(),
    refetchInterval: false, // Disable auto-refresh to prevent errors
    retry: false,
  });
}

export function useTests(params?: {
  test_type?: string;
  status?: string;
  enabled?: boolean;
}) {
  return useQuery({
    queryKey: ['tests', params],
    queryFn: () => apiClient.getTests(params),
    retry: false,
  });
}

export function useTest(testId: string) {
  return useQuery({
    queryKey: ['tests', testId],
    queryFn: () => apiClient.getTest(testId),
    enabled: !!testId,
    retry: false,
  });
}

export function useCreateTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (test: Partial<Test>) => apiClient.createTest(test),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tests'] });
    },
  });
}

export function useUpdateTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ testId, test }: { testId: string; test: Partial<Test> }) =>
      apiClient.updateTest(testId, test),
    onSuccess: (_, { testId }) => {
      queryClient.invalidateQueries({ queryKey: ['tests'] });
      queryClient.invalidateQueries({ queryKey: ['tests', testId] });
    },
  });
}

export function useDeleteTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (testId: string) => apiClient.deleteTest(testId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tests'] });
    },
  });
}

export function useRunTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (testId: string) => apiClient.runTest(testId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tests'] });
      queryClient.invalidateQueries({ queryKey: ['executions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useConnections() {
  return useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.getConnections(),
    retry: false,
  });
}

export function useExecutions(params?: {
  test_id?: string;
  status?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['executions', params],
    queryFn: () => apiClient.getExecutions(params),
    retry: false,
  });
}
