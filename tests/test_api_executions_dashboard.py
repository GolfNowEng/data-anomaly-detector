"""
Tests for executions and dashboard API endpoints
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestExecutionsAPI:
    """Tests for /v1/executions endpoints"""

    @pytest.fixture
    def mock_results_client(self):
        """Mock TimescaleDB results client"""
        with patch('api.routers.executions.results_client') as mock:
            yield mock

    @pytest.fixture
    def sample_execution(self):
        """Sample execution result for testing"""
        return {
            'execution_id': 'exec-123',
            'test_id': 'vol_001_test',
            'status': 'passed',
            'started_at': datetime.utcnow().isoformat(),
            'completed_at': datetime.utcnow().isoformat(),
            'duration_ms': 1250,
            'result_summary': {'count': 500, 'is_anomaly': False},
            'expected_values': {'min_count': 100},
            'actual_values': {'count': 500},
            'rows_processed': 1
        }

    def test_list_executions_all(self, app_client, mock_results_client, sample_execution):
        """Test listing all executions"""
        mock_results_client.list_executions.return_value = [sample_execution]

        response = app_client.get("/v1/executions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['execution_id'] == 'exec-123'

    def test_list_executions_filter_by_test_id(self, app_client, mock_results_client, sample_execution):
        """Test filtering executions by test ID"""
        mock_results_client.list_executions.return_value = [sample_execution]

        response = app_client.get("/v1/executions?test_id=vol_001_test")

        assert response.status_code == 200
        mock_results_client.list_executions.assert_called_with(
            test_id='vol_001_test',
            status=None,
            limit=50
        )

    def test_list_executions_filter_by_status(self, app_client, mock_results_client, sample_execution):
        """Test filtering executions by status"""
        mock_results_client.list_executions.return_value = [sample_execution]

        response = app_client.get("/v1/executions?status=passed")

        assert response.status_code == 200
        mock_results_client.list_executions.assert_called_with(
            test_id=None,
            status='passed',
            limit=50
        )

    def test_list_executions_with_limit(self, app_client, mock_results_client, sample_execution):
        """Test listing executions with custom limit"""
        mock_results_client.list_executions.return_value = [sample_execution]

        response = app_client.get("/v1/executions?limit=10")

        assert response.status_code == 200
        mock_results_client.list_executions.assert_called_with(
            test_id=None,
            status=None,
            limit=10
        )

    def test_list_executions_empty(self, app_client, mock_results_client):
        """Test listing executions when none exist"""
        mock_results_client.list_executions.return_value = []

        response = app_client.get("/v1/executions")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_execution_success(self, app_client, mock_results_client, sample_execution):
        """Test getting a specific execution"""
        mock_results_client.get_execution.return_value = sample_execution

        response = app_client.get("/v1/executions/exec-123")

        assert response.status_code == 200
        data = response.json()
        assert data['execution_id'] == 'exec-123'

    def test_get_execution_not_found(self, app_client, mock_results_client):
        """Test getting a non-existent execution"""
        mock_results_client.get_execution.return_value = None

        response = app_client.get("/v1/executions/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()['detail']


class TestDashboardAPI:
    """Tests for /v1/dashboard endpoints"""

    @pytest.fixture
    def mock_results_client(self):
        """Mock TimescaleDB results client"""
        with patch('api.routers.dashboard.results_client') as mock:
            yield mock

    @pytest.fixture
    def sample_summary(self):
        """Sample dashboard summary for testing"""
        return {
            'total_tests': 100,
            'passed': 85,
            'failed': 10,
            'error': 5,
            'pass_rate': 85.0,
            'last_24h_executions': 250,
            'critical_failures': 2
        }

    def test_get_dashboard_summary_success(self, app_client, mock_results_client, sample_summary):
        """Test getting dashboard summary"""
        mock_results_client.get_dashboard_summary.return_value = sample_summary

        response = app_client.get("/v1/dashboard/summary")

        assert response.status_code == 200
        data = response.json()
        assert data['total_tests'] == 100
        assert data['pass_rate'] == 85.0

    def test_get_dashboard_summary_error(self, app_client, mock_results_client):
        """Test dashboard summary handles errors gracefully"""
        mock_results_client.get_dashboard_summary.side_effect = Exception("Database error")

        response = app_client.get("/v1/dashboard/summary")

        assert response.status_code == 500
        assert "Failed to fetch dashboard summary" in response.json()['detail']
