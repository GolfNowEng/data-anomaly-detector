import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle2, XCircle, Loader2, Clock, LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatusCardsProps {
  passed: number;
  failed: number;
  running: number;
  pending: number;
}

interface StatusConfig {
  key: 'passed' | 'failed' | 'running' | 'pending';
  label: string;
  icon: LucideIcon;
  color: string;
  bgColor: string;
  animate?: boolean;
}

const statuses: StatusConfig[] = [
  {
    key: 'passed',
    label: 'Passed',
    icon: CheckCircle2,
    color: 'text-status-passed',
    bgColor: 'bg-green-50',
  },
  {
    key: 'failed',
    label: 'Failed',
    icon: XCircle,
    color: 'text-status-failed',
    bgColor: 'bg-red-50',
  },
  {
    key: 'running',
    label: 'Running',
    icon: Loader2,
    color: 'text-status-running',
    bgColor: 'bg-blue-50',
    animate: true,
  },
  {
    key: 'pending',
    label: 'Pending',
    icon: Clock,
    color: 'text-status-pending',
    bgColor: 'bg-gray-50',
  },
];

export function StatusCards({ passed, failed, running, pending }: StatusCardsProps) {
  const counts = { passed, failed, running, pending };

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {statuses.map((status) => (
        <Card key={status.key} className={cn(status.bgColor)}>
          <CardContent className="flex items-center gap-4 p-4">
            <div className={cn('rounded-full p-2', status.bgColor)}>
              <status.icon
                className={cn(
                  'h-6 w-6',
                  status.color,
                  status.animate && 'animate-spin'
                )}
              />
            </div>
            <div>
              <p className="text-2xl font-bold">{counts[status.key]}</p>
              <p className="text-sm text-muted-foreground">{status.label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
