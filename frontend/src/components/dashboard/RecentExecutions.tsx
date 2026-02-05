import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { formatRelativeTime } from '@/lib/utils';
import type { Execution, TestStatus } from '@/types';
import { Link } from 'react-router-dom';

interface RecentExecutionsProps {
  executions: Execution[];
}

export function RecentExecutions({ executions }: RecentExecutionsProps) {
  const executionList = executions || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Executions</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Test</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Result</TableHead>
              <TableHead className="text-right">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {executionList.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="text-center text-muted-foreground"
                >
                  No recent executions
                </TableCell>
              </TableRow>
            ) : (
              executionList.map((execution) => (
                <TableRow key={execution.execution_id}>
                  <TableCell>
                    <Link
                      to={`/tests/${execution.test_id}`}
                      className="font-medium hover:underline"
                    >
                      {execution.test_name || execution.test_id}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge variant={execution.status as TestStatus}>
                      {execution.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {execution.result_value !== undefined && (
                      <span className="font-mono text-sm">
                        {execution.result_value.toLocaleString()}
                        {execution.expected_value !== undefined && (
                          <span className="text-muted-foreground">
                            {' '}
                            / {execution.expected_value.toLocaleString()}
                          </span>
                        )}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {formatRelativeTime(execution.started_at)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
