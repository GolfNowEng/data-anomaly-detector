import axios, { AxiosError, AxiosInstance } from 'axios';
import type { Test, Connection, Execution, DashboardSummary, PaginatedResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Dashboard
  async getDashboardSummary(): Promise<DashboardSummary> {
    const { data } = await this.client.get('/dashboard/summary');
    return data;
  }

  // Tests
  async getTests(params?: {
    test_type?: string;
    status?: string;
    enabled?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Test>> {
    const { data } = await this.client.get('/tests', { params });
    return data;
  }

  async getTest(testId: string): Promise<Test> {
    const { data } = await this.client.get(`/tests/${testId}`);
    return data;
  }

  async createTest(test: Partial<Test>): Promise<Test> {
    const { data } = await this.client.post('/tests', test);
    return data;
  }

  async updateTest(testId: string, test: Partial<Test>): Promise<Test> {
    const { data } = await this.client.put(`/tests/${testId}`, test);
    return data;
  }

  async deleteTest(testId: string): Promise<void> {
    await this.client.delete(`/tests/${testId}`);
  }

  async runTest(testId: string): Promise<{ execution_id: string }> {
    const { data } = await this.client.post(`/tests/${testId}/run`);
    return data;
  }

  // Connections
  async getConnections(): Promise<Connection[]> {
    const { data } = await this.client.get('/connections');
    return data;
  }

  async getConnection(connectionId: string): Promise<Connection> {
    const { data } = await this.client.get(`/connections/${connectionId}`);
    return data;
  }

  async createConnection(connection: Partial<Connection> & { password: string }): Promise<Connection> {
    const { data } = await this.client.post('/connections', connection);
    return data;
  }

  async deleteConnection(connectionId: string): Promise<void> {
    await this.client.delete(`/connections/${connectionId}`);
  }

  async testConnection(connectionId: string): Promise<{ success: boolean; message: string }> {
    const { data } = await this.client.post(`/connections/${connectionId}/test`);
    return data;
  }

  // Executions
  async getExecutions(params?: {
    test_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<Execution[]> {
    const { data } = await this.client.get('/executions', { params });
    return data;
  }

  async getExecution(executionId: string): Promise<Execution> {
    const { data } = await this.client.get(`/executions/${executionId}`);
    return data;
  }
}

export const apiClient = new ApiClient();
