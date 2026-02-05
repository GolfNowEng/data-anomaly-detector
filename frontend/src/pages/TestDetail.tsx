import { useParams, useNavigate, Link } from 'react-router-dom';
import { Header } from '@/components/layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useTest, useExecutions, useRunTest, useDeleteTest } from '@/hooks';
import { formatDateTime, formatRelativeTime, TEST_TYPE_LABELS } from '@/lib/utils';
import {
  Play,
  Edit,
  Trash2,
  Loader2,
  ArrowLeft,
  Clock,
  Database,
  Mail,
} from 'lucide-react';
import type { TestStatus, Severity, Execution } from '@/types';

// Mock data
const mockTest = {
  test_id: 'test-1',
  name: 'Daily Orders Volume',
  description: 'Checks that daily order count is within expected range compared to the same day last week',
  test_type: 'volume' as const,
  connection_id: 'conn-1',
  connection_name: 'Production DB',
  query: `SELECT COUNT(*)
FROM orders
WHERE created_at >= DATEADD(day, -1, GETDATE())
  AND status != 'cancelled'`,
  enabled: true,
  severity: 'critical' as const,
  alert_emails: ['team@example.com', 'oncall@example.com'],
  config: {
    comparison_type: 'day_over_day' as const,
    threshold_percent: 15,
  },
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
  last_run: new Date(Date.now() - 1800000).toISOString(),
  last_status: 'passed' as const,
};

const mockExecutions: Execution[] = [
  {
    execution_id: 'exec-1',
    test_id: 'test-1',
    status: 'passed',
    started_at: new Date(Date.now() - 1800000).toISOString(),
    completed_at: new Date(Date.now() - 1795000).toISOString(),
    result_value: 15420,
    expected_value: 15000,
    threshold: 15,
  },
  {
    execution_id: 'exec-2',
    test_id: 'test-1',
    status: 'passed',
    started_at: new Date(Date.now() - 86400000).toISOString(),
    completed_at: new Date(Date.now() - 86395000).toISOString(),
    result_value: 14980,
    expected_value: 15200,
    threshold: 15,
  },
  {
    execution_id: 'exec-3',
    test_id: 'test-1',
    status: 'failed',
    started_at: new Date(Date.now() - 172800000).toISOString(),
    completed_at: new Date(Date.now() - 172795000).toISOString(),
    result_value: 8500,
    expected_value: 15100,
    threshold: 15,
    error_message: 'Value 43.7% below expected threshold',
  },
];

export function TestDetail() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const { data: test, isLoading: testLoading } = useTest(testId!);
  const { data: executions, isLoading: executionsLoading } = useExecutions({
    test_id: testId,
    limit: 20,
  });
  const runTestMutation = useRunTest();
  const deleteTestMutation = useDeleteTest();

  // Use mock data if API not available
  const testData = test || mockTest;
  const executionsData = executions || mockExecutions;

  const handleRun = async () => {
    if (testId) {
      await runTestMutation.mutateAsync(testId);
    }
  };

  const handleDelete = async () => {
    if (testId && confirm('Are you sure you want to delete this test?')) {
      await deleteTestMutation.mutateAsync(testId);
      navigate('/tests');
    }
  };

  if (testLoading && !test) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header
        title={testData.name}
        description={testData.description}
        actions={
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleRun}
              disabled={runTestMutation.isPending}
            >
              {runTestMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Run
            </Button>
            <Link to={`/tests/${testId}/edit`}>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </Link>
            <Button
              variant="outline"
              onClick={handleDelete}
              disabled={deleteTestMutation.isPending}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        }
      />

      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <Link
          to="/tests"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Tests
        </Link>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant={testData.last_status as TestStatus} className="text-lg">
                {testData.last_status || 'Never Run'}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Last Run
              </CardTitle>
            </CardHeader>
            <CardContent className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span>
                {testData.last_run
                  ? formatRelativeTime(testData.last_run)
                  : 'Never'}
              </span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Severity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant={testData.severity as Severity}>
                {testData.severity}
              </Badge>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="details">
          <TabsList>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="history">Execution History</TabsTrigger>
            <TabsTrigger value="query">Query</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Test Type
                    </p>
                    <p>{TEST_TYPE_LABELS[testData.test_type]}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Connection
                    </p>
                    <p className="flex items-center gap-2">
                      <Database className="h-4 w-4" />
                      {testData.connection_name || testData.connection_id}
                    </p>
                  </div>
                  {testData.config.comparison_type && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Comparison
                      </p>
                      <p className="capitalize">
                        {testData.config.comparison_type.replace(/_/g, ' ')}
                      </p>
                    </div>
                  )}
                  {testData.config.threshold_percent !== undefined && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Threshold
                      </p>
                      <p>{testData.config.threshold_percent}%</p>
                    </div>
                  )}
                </div>
                {testData.alert_emails && testData.alert_emails.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">
                      Alert Recipients
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {testData.alert_emails.map((email) => (
                        <Badge key={email} variant="outline">
                          <Mail className="h-3 w-3 mr-1" />
                          {email}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>Execution History</CardTitle>
              </CardHeader>
              <CardContent>
                {executionsLoading && !executions ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Status</TableHead>
                        <TableHead>Result</TableHead>
                        <TableHead>Expected</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Duration</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {executionsData.length === 0 ? (
                        <TableRow>
                          <TableCell
                            colSpan={5}
                            className="text-center text-muted-foreground"
                          >
                            No executions yet
                          </TableCell>
                        </TableRow>
                      ) : (
                        executionsData.map((exec) => (
                          <TableRow key={exec.execution_id}>
                            <TableCell>
                              <Badge variant={exec.status as TestStatus}>
                                {exec.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono">
                              {exec.result_value?.toLocaleString() ?? '-'}
                            </TableCell>
                            <TableCell className="font-mono text-muted-foreground">
                              {exec.expected_value?.toLocaleString() ?? '-'}
                            </TableCell>
                            <TableCell>{formatDateTime(exec.started_at)}</TableCell>
                            <TableCell>
                              {exec.completed_at
                                ? `${Math.round(
                                    (new Date(exec.completed_at).getTime() -
                                      new Date(exec.started_at).getTime()) /
                                      1000
                                  )}s`
                                : '-'}
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="query">
            <Card>
              <CardHeader>
                <CardTitle>SQL Query</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono">
                  {testData.query}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
