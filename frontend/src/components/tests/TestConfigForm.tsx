import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { Test, Connection } from '@/types';
import { TEST_TYPE_LABELS } from '@/lib/utils';

const testSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  test_type: z.enum(['volume', 'distribution', 'uniqueness', 'referential', 'pattern', 'freshness']),
  connection_id: z.string().min(1, 'Connection is required'),
  query: z.string().min(1, 'Query is required'),
  severity: z.enum(['critical', 'high', 'medium', 'low']),
  alert_emails: z.string().optional(),
  // Volume config
  comparison_type: z.string().optional(),
  threshold_percent: z.coerce.number().optional(),
  min_expected: z.coerce.number().optional(),
  max_expected: z.coerce.number().optional(),
});

type TestFormData = z.infer<typeof testSchema>;

interface TestConfigFormProps {
  test?: Test;
  connections: Connection[];
  onSubmit: (data: Partial<Test>) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export function TestConfigForm({
  test,
  connections,
  onSubmit,
  onCancel,
  isSubmitting,
}: TestConfigFormProps) {
  const [testType, setTestType] = useState(test?.test_type || 'volume');

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<TestFormData>({
    resolver: zodResolver(testSchema),
    defaultValues: {
      name: test?.name || '',
      description: test?.description || '',
      test_type: test?.test_type || 'volume',
      connection_id: test?.connection_id || '',
      query: test?.query || '',
      severity: test?.severity || 'medium',
      alert_emails: test?.alert_emails?.join(', ') || '',
      comparison_type: test?.config?.comparison_type || 'day_over_day',
      threshold_percent: test?.config?.threshold_percent || 10,
      min_expected: test?.config?.min_expected,
      max_expected: test?.config?.max_expected,
    },
  });

  const onFormSubmit = (data: TestFormData) => {
    const testData: Partial<Test> = {
      name: data.name,
      description: data.description,
      test_type: data.test_type,
      connection_id: data.connection_id,
      query: data.query,
      severity: data.severity,
      alert_emails: data.alert_emails?.split(',').map((e) => e.trim()).filter(Boolean),
      enabled: true,
      config: {},
    };

    // Add type-specific config
    if (data.test_type === 'volume') {
      testData.config = {
        comparison_type: data.comparison_type as Test['config']['comparison_type'],
        threshold_percent: data.threshold_percent,
        min_expected: data.min_expected,
        max_expected: data.max_expected,
      };
    }

    onSubmit(testData);
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      <Tabs defaultValue="basic">
        <TabsList>
          <TabsTrigger value="basic">Basic Info</TabsTrigger>
          <TabsTrigger value="query">Query</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Test Name</Label>
                <Input
                  id="name"
                  {...register('name')}
                  placeholder="e.g., Daily Orders Volume Check"
                />
                {errors.name && (
                  <p className="text-sm text-red-500">{errors.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  {...register('description')}
                  placeholder="Describe what this test validates"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Test Type</Label>
                  <Select
                    value={testType}
                    onValueChange={(value) => {
                      setTestType(value as Test['test_type']);
                      setValue('test_type', value as Test['test_type']);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(TEST_TYPE_LABELS).map(([key, label]) => (
                        <SelectItem key={key} value={key}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Severity</Label>
                  <Select
                    defaultValue={test?.severity || 'medium'}
                    onValueChange={(value) =>
                      setValue('severity', value as Test['severity'])
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Connection</Label>
                <Select
                  defaultValue={test?.connection_id}
                  onValueChange={(value) => setValue('connection_id', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a connection" />
                  </SelectTrigger>
                  <SelectContent>
                    {connections.map((conn) => (
                      <SelectItem key={conn.connection_id} value={conn.connection_id}>
                        {conn.name} ({conn.db_type})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.connection_id && (
                  <p className="text-sm text-red-500">
                    {errors.connection_id.message}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="query" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>SQL Query</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="query">Query (must return a single numeric value)</Label>
                <textarea
                  id="query"
                  {...register('query')}
                  className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="SELECT COUNT(*) FROM orders WHERE created_at >= DATEADD(day, -1, GETDATE())"
                />
                {errors.query && (
                  <p className="text-sm text-red-500">{errors.query.message}</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {testType === 'volume' && (
                <>
                  <div className="space-y-2">
                    <Label>Comparison Type</Label>
                    <Select
                      defaultValue={test?.config?.comparison_type || 'day_over_day'}
                      onValueChange={(value) => setValue('comparison_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="day_over_day">Day over Day</SelectItem>
                        <SelectItem value="week_over_week">Week over Week</SelectItem>
                        <SelectItem value="year_over_year">Year over Year</SelectItem>
                        <SelectItem value="absolute">Absolute Threshold</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="threshold_percent">Threshold Percent</Label>
                    <Input
                      id="threshold_percent"
                      type="number"
                      {...register('threshold_percent')}
                      placeholder="10"
                    />
                    <p className="text-xs text-muted-foreground">
                      Alert when result differs by more than this percentage
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="min_expected">Min Expected</Label>
                      <Input
                        id="min_expected"
                        type="number"
                        {...register('min_expected')}
                        placeholder="Optional"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="max_expected">Max Expected</Label>
                      <Input
                        id="max_expected"
                        type="number"
                        {...register('max_expected')}
                        placeholder="Optional"
                      />
                    </div>
                  </div>
                </>
              )}

              {testType !== 'volume' && (
                <p className="text-muted-foreground text-center py-4">
                  Configuration for {TEST_TYPE_LABELS[testType]} tests coming soon.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Alert Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="alert_emails">Alert Email Recipients</Label>
                <Input
                  id="alert_emails"
                  {...register('alert_emails')}
                  placeholder="email1@example.com, email2@example.com"
                />
                <p className="text-xs text-muted-foreground">
                  Comma-separated list of email addresses
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end gap-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : test ? 'Update Test' : 'Create Test'}
        </Button>
      </div>
    </form>
  );
}
