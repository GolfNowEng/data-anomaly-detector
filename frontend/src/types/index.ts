// Test configuration types
export type TestType = 'volume' | 'distribution' | 'uniqueness' | 'referential' | 'pattern' | 'freshness';
export type TestStatus = 'passed' | 'failed' | 'running' | 'pending';
export type Severity = 'critical' | 'high' | 'medium' | 'low';

export interface Test {
  test_id: string;
  name: string;
  description?: string;
  test_type: TestType;
  connection_id: string;
  connection_name?: string;
  query: string;
  schedule?: string;
  enabled: boolean;
  severity: Severity;
  alert_emails?: string[];
  config: TestConfig;
  created_at: string;
  updated_at: string;
  last_run?: string;
  last_status?: TestStatus;
}

export interface TestConfig {
  // Volume test config
  comparison_type?: 'day_over_day' | 'week_over_week' | 'year_over_year' | 'absolute';
  threshold_percent?: number;
  min_expected?: number;
  max_expected?: number;

  // Distribution test config
  columns?: string[];
  expected_distribution?: Record<string, number>;
  tolerance_percent?: number;

  // Uniqueness test config
  unique_columns?: string[];

  // Pattern test config
  pattern?: string;
  pattern_column?: string;

  // Freshness test config
  timestamp_column?: string;
  max_age_hours?: number;
}

export interface Connection {
  connection_id: string;
  name: string;
  db_type: 'sqlserver' | 'postgres';
  host: string;
  port: number;
  database: string;
  username: string;
  created_at: string;
}

export interface Execution {
  execution_id: string;
  test_id: string;
  test_name?: string;
  status: TestStatus;
  started_at: string;
  completed_at?: string;
  result_value?: number;
  expected_value?: number;
  threshold?: number;
  error_message?: string;
  sample_records?: Record<string, unknown>[];
  metadata?: Record<string, unknown>;
}

export interface DashboardSummary {
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  running_tests: number;
  pending_tests: number;
  health_score: number;
  recent_executions: Execution[];
  critical_alerts: Execution[];
  trends: TrendData[];
}

export interface TrendData {
  date: string;
  passed: number;
  failed: number;
  total: number;
  pass_rate: number;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}
