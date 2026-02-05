import { Header } from '@/components/layout';
import {
  HealthScoreRing,
  StatusCards,
  AlertsPanel,
  TrendsChart,
  RecentExecutions,
} from '@/components/dashboard';
import { useDashboardSummary } from '@/hooks';
import { Loader2 } from 'lucide-react';

// Mock data for development when API is not available
const mockDashboardData = {
  total_tests: 24,
  passed_tests: 18,
  failed_tests: 3,
  running_tests: 1,
  pending_tests: 2,
  health_score: 85,
  recent_executions: [
    {
      execution_id: '1',
      test_id: 'test-1',
      test_name: 'Daily Orders Volume',
      status: 'passed' as const,
      started_at: new Date().toISOString(),
      result_value: 15420,
      expected_value: 15000,
    },
    {
      execution_id: '2',
      test_id: 'test-2',
      test_name: 'User Registration Check',
      status: 'failed' as const,
      started_at: new Date(Date.now() - 3600000).toISOString(),
      result_value: 45,
      expected_value: 100,
      error_message: 'Value below threshold',
    },
    {
      execution_id: '3',
      test_id: 'test-3',
      test_name: 'Payment Processing',
      status: 'passed' as const,
      started_at: new Date(Date.now() - 7200000).toISOString(),
      result_value: 9823,
      expected_value: 10000,
    },
  ],
  critical_alerts: [
    {
      execution_id: '2',
      test_id: 'test-2',
      test_name: 'User Registration Check',
      status: 'failed' as const,
      started_at: new Date(Date.now() - 3600000).toISOString(),
      error_message: 'Value 55% below expected threshold',
    },
  ],
  trends: [
    { date: 'Mon', passed: 22, failed: 2, total: 24, pass_rate: 92 },
    { date: 'Tue', passed: 20, failed: 4, total: 24, pass_rate: 83 },
    { date: 'Wed', passed: 23, failed: 1, total: 24, pass_rate: 96 },
    { date: 'Thu', passed: 21, failed: 3, total: 24, pass_rate: 87 },
    { date: 'Fri', passed: 19, failed: 5, total: 24, pass_rate: 79 },
    { date: 'Sat', passed: 22, failed: 2, total: 24, pass_rate: 92 },
    { date: 'Sun', passed: 18, failed: 3, total: 21, pass_rate: 86 },
  ],
};

export function Dashboard() {
  const { data, isLoading, error } = useDashboardSummary();

  // Use mock data if API fails or is loading, with safe defaults
  const dashboardData = {
    ...mockDashboardData,
    ...data,
    // Ensure arrays are never undefined
    recent_executions: data?.recent_executions || mockDashboardData.recent_executions,
    critical_alerts: data?.critical_alerts || mockDashboardData.critical_alerts,
    trends: data?.trends || mockDashboardData.trends,
  };

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Dashboard"
        description="Monitor your data quality at a glance"
      />
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {isLoading && !data ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error && !data ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              Using sample data - connect to API for live data
            </p>
          </div>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-[auto_1fr]">
          <div className="flex justify-center">
            <HealthScoreRing score={dashboardData.health_score} />
          </div>
          <StatusCards
            passed={dashboardData.passed_tests}
            failed={dashboardData.failed_tests}
            running={dashboardData.running_tests}
            pending={dashboardData.pending_tests}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
          <TrendsChart data={dashboardData.trends} />
          <AlertsPanel alerts={dashboardData.critical_alerts} />
        </div>

        <RecentExecutions executions={dashboardData.recent_executions} />
      </div>
    </div>
  );
}
