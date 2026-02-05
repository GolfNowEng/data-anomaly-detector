import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { formatRelativeTime } from '@/lib/utils';
import type { Execution } from '@/types';
import { Link } from 'react-router-dom';

interface AlertsPanelProps {
  alerts: Execution[];
}

export function AlertsPanel({ alerts }: AlertsPanelProps) {
  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Critical Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-sm text-muted-foreground py-4">
            No critical alerts
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          Critical Alerts
          <Badge variant="failed" className="ml-2">
            {alerts.length}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {alerts.map((alert) => (
          <Link
            key={alert.execution_id}
            to={`/tests/${alert.test_id}`}
            className="block rounded-lg border border-red-200 bg-red-50 p-3 hover:bg-red-100 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-red-900">
                  {alert.test_name || alert.test_id}
                </p>
                <p className="text-sm text-red-700 mt-1">
                  {alert.error_message || 'Test failed'}
                </p>
              </div>
              <span className="text-xs text-red-600">
                {formatRelativeTime(alert.started_at)}
              </span>
            </div>
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}
