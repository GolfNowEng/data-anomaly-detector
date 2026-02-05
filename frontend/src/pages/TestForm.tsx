import { useNavigate, useParams } from 'react-router-dom';
import { Header } from '@/components/layout';
import { TestConfigForm } from '@/components/tests';
import { useTest, useCreateTest, useUpdateTest, useConnections } from '@/hooks';
import { Loader2 } from 'lucide-react';
import type { Test } from '@/types';

// Mock connections for development
const mockConnections = [
  {
    connection_id: 'conn-1',
    name: 'Production DB',
    db_type: 'sqlserver' as const,
    host: 'prod-server',
    port: 1433,
    database: 'production',
    username: 'reader',
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    connection_id: 'conn-2',
    name: 'Analytics DB',
    db_type: 'postgres' as const,
    host: 'analytics-server',
    port: 5432,
    database: 'analytics',
    username: 'analyst',
    created_at: '2024-01-02T00:00:00Z',
  },
];

export function TestForm() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const isEditing = !!testId;

  const { data: test, isLoading: testLoading } = useTest(testId!);
  const { data: connections, isLoading: connectionsLoading } = useConnections();
  const createTestMutation = useCreateTest();
  const updateTestMutation = useUpdateTest();

  const connectionsData = connections || mockConnections;

  const handleSubmit = async (data: Partial<Test>) => {
    try {
      if (isEditing) {
        await updateTestMutation.mutateAsync({ testId: testId!, test: data });
      } else {
        await createTestMutation.mutateAsync(data);
      }
      navigate('/tests');
    } catch (error) {
      console.error('Failed to save test:', error);
    }
  };

  const handleCancel = () => {
    navigate('/tests');
  };

  if ((isEditing && testLoading) || connectionsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header
        title={isEditing ? 'Edit Test' : 'Create Test'}
        description={
          isEditing
            ? 'Modify your test configuration'
            : 'Configure a new data quality test'
        }
      />
      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-3xl mx-auto">
          <TestConfigForm
            test={test}
            connections={connectionsData}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isSubmitting={
              createTestMutation.isPending || updateTestMutation.isPending
            }
          />
        </div>
      </div>
    </div>
  );
}
