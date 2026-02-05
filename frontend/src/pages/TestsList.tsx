import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Header } from '@/components/layout';
import { TestFilters, TestList } from '@/components/tests';
import { Button } from '@/components/ui/button';
import { Plus, Loader2 } from 'lucide-react';
import { useTests, useRunTest } from '@/hooks';
import type { Test } from '@/types';

// Mock data for development
const mockTests: Test[] = [
  {
    test_id: 'test-1',
    name: 'Daily Orders Volume',
    description: 'Checks that daily order count is within expected range',
    test_type: 'volume',
    connection_id: 'conn-1',
    connection_name: 'Production DB',
    query: 'SELECT COUNT(*) FROM orders WHERE created_at >= DATEADD(day, -1, GETDATE())',
    enabled: true,
    severity: 'critical',
    config: { comparison_type: 'day_over_day', threshold_percent: 15 },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
    last_run: new Date(Date.now() - 1800000).toISOString(),
    last_status: 'passed',
  },
  {
    test_id: 'test-2',
    name: 'User Registration Check',
    description: 'Monitors new user registrations',
    test_type: 'volume',
    connection_id: 'conn-1',
    connection_name: 'Production DB',
    query: 'SELECT COUNT(*) FROM users WHERE created_at >= DATEADD(day, -1, GETDATE())',
    enabled: true,
    severity: 'high',
    config: { comparison_type: 'week_over_week', threshold_percent: 20 },
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-14T00:00:00Z',
    last_run: new Date(Date.now() - 3600000).toISOString(),
    last_status: 'failed',
  },
  {
    test_id: 'test-3',
    name: 'Payment Processing',
    description: 'Validates payment transaction volumes',
    test_type: 'volume',
    connection_id: 'conn-2',
    connection_name: 'Analytics DB',
    query: 'SELECT SUM(amount) FROM payments WHERE created_at >= DATEADD(day, -1, GETDATE())',
    enabled: true,
    severity: 'critical',
    config: { comparison_type: 'day_over_day', threshold_percent: 10 },
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-13T00:00:00Z',
    last_run: new Date(Date.now() - 7200000).toISOString(),
    last_status: 'passed',
  },
  {
    test_id: 'test-4',
    name: 'Inventory Levels',
    description: 'Monitors product inventory counts',
    test_type: 'volume',
    connection_id: 'conn-1',
    connection_name: 'Production DB',
    query: 'SELECT COUNT(*) FROM inventory WHERE quantity < 10',
    enabled: true,
    severity: 'medium',
    config: { comparison_type: 'absolute', min_expected: 0, max_expected: 50 },
    created_at: '2024-01-04T00:00:00Z',
    updated_at: '2024-01-12T00:00:00Z',
    last_status: 'pending',
  },
];

export function TestsList() {
  const [search, setSearch] = useState('');
  const [testType, setTestType] = useState('all');
  const [status, setStatus] = useState('all');
  const [severity, setSeverity] = useState('all');
  const [runningTests, setRunningTests] = useState<Set<string>>(new Set());

  const { data, isLoading, error } = useTests();
  const runTestMutation = useRunTest();

  // Use mock data if API is not available
  const tests = data?.items || mockTests;

  const filteredTests = useMemo(() => {
    return tests.filter((test) => {
      if (search && !test.name.toLowerCase().includes(search.toLowerCase())) {
        return false;
      }
      if (testType !== 'all' && test.test_type !== testType) {
        return false;
      }
      if (status !== 'all' && test.last_status !== status) {
        return false;
      }
      if (severity !== 'all' && test.severity !== severity) {
        return false;
      }
      return true;
    });
  }, [tests, search, testType, status, severity]);

  const handleRunTest = async (testId: string) => {
    setRunningTests((prev) => new Set(prev).add(testId));
    try {
      await runTestMutation.mutateAsync(testId);
    } finally {
      setRunningTests((prev) => {
        const next = new Set(prev);
        next.delete(testId);
        return next;
      });
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Tests"
        description="Manage and monitor your data quality tests"
        actions={
          <Link to="/tests/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Test
            </Button>
          </Link>
        }
      />
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <TestFilters
          search={search}
          onSearchChange={setSearch}
          testType={testType}
          onTestTypeChange={setTestType}
          status={status}
          onStatusChange={setStatus}
          severity={severity}
          onSeverityChange={setSeverity}
        />

        {isLoading && !data ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error && !data ? (
          <div className="text-center py-4 text-sm text-muted-foreground">
            Using sample data - connect to API for live data
          </div>
        ) : null}

        <TestList
          tests={filteredTests}
          onRunTest={handleRunTest}
          runningTests={runningTests}
        />
      </div>
    </div>
  );
}
