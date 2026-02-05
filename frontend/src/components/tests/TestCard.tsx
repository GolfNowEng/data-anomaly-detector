import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Play, Clock, Database } from 'lucide-react';
import { formatRelativeTime, TEST_TYPE_LABELS } from '@/lib/utils';
import type { Test, TestStatus, Severity } from '@/types';
import { Link } from 'react-router-dom';

interface TestCardProps {
  test: Test;
  onRun?: (testId: string) => void;
  isRunning?: boolean;
}

export function TestCard({ test, onRun, isRunning }: TestCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <Link
              to={`/tests/${test.test_id}`}
              className="font-semibold hover:underline"
            >
              {test.name}
            </Link>
            {test.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {test.description}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Badge variant={test.severity as Severity}>{test.severity}</Badge>
            {test.last_status && (
              <Badge variant={test.last_status as TestStatus}>
                {test.last_status}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Database className="h-4 w-4" />
              {test.connection_name || test.connection_id.slice(0, 8)}
            </span>
            <Badge variant="outline">{TEST_TYPE_LABELS[test.test_type]}</Badge>
          </div>
          <div className="flex items-center gap-2">
            {test.last_run && (
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {formatRelativeTime(test.last_run)}
              </span>
            )}
            <Button
              size="sm"
              variant="outline"
              onClick={() => onRun?.(test.test_id)}
              disabled={isRunning}
            >
              <Play className="h-4 w-4 mr-1" />
              Run
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
