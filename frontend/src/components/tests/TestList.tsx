import { TestCard } from './TestCard';
import type { Test } from '@/types';

interface TestListProps {
  tests: Test[];
  onRunTest: (testId: string) => void;
  runningTests: Set<string>;
}

export function TestList({ tests, onRunTest, runningTests }: TestListProps) {
  if (tests.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-lg font-medium text-muted-foreground">No tests found</p>
        <p className="text-sm text-muted-foreground">
          Try adjusting your filters or create a new test
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {tests.map((test) => (
        <TestCard
          key={test.test_id}
          test={test}
          onRun={onRunTest}
          isRunning={runningTests.has(test.test_id)}
        />
      ))}
    </div>
  );
}
