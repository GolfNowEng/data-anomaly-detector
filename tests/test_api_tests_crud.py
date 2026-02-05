"""
Tests for test configuration CRUD API endpoints
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestCreateTest:
    """Tests for POST /v1/tests endpoint"""

    def test_create_test_success(self, app_client, sample_test_config):
        """Test successful test creation"""
        with patch('api.routers.tests.db_client') as mock_db:
            # Mock: test doesn't exist yet
            mock_db.get_test.return_value = None
            mock_db.create_test.return_value = sample_test_config

            payload = {
                'test_id': 'vol_001_test',
                'name': 'Test Volume Check',
                'description': 'Test description',
                'test_type': 'volume',
                'enabled': True,
                'severity': 'high',
                'connection_id': 'test_connection',
                'query': 'SELECT COUNT(*) as count FROM test_table',
                'parameters': {'anomaly_threshold_min': 100},
                'tags': ['test']
            }

            response = app_client.post("/v1/tests", json=payload)

            assert response.status_code == 201
            data = response.json()
            assert data['test_id'] == 'vol_001_test'
            assert data['name'] == 'Test Volume Check'

    def test_create_test_conflict(self, app_client, sample_test_config):
        """Test creating a test that already exists returns 409"""
        with patch('api.routers.tests.db_client') as mock_db:
            # Mock: test already exists
            mock_db.get_test.return_value = sample_test_config

            payload = {
                'test_id': 'vol_001_test',
                'name': 'Test Volume Check',
                'test_type': 'volume',
                'severity': 'high',
                'connection_id': 'test_connection',
                'query': 'SELECT COUNT(*) as count FROM test_table'
            }

            response = app_client.post("/v1/tests", json=payload)

            assert response.status_code == 409
            assert "already exists" in response.json()['detail']

    def test_create_test_missing_required_fields(self, app_client):
        """Test creating a test with missing required fields returns 422"""
        payload = {
            'test_id': 'vol_001_test',
            'name': 'Test Volume Check'
            # Missing: test_type, severity, connection_id, query
        }

        response = app_client.post("/v1/tests", json=payload)

        assert response.status_code == 422


class TestGetTest:
    """Tests for GET /v1/tests/{test_id} endpoint"""

    def test_get_test_success(self, app_client, sample_test_config):
        """Test successful test retrieval"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = sample_test_config

            response = app_client.get("/v1/tests/vol_001_test")

            assert response.status_code == 200
            data = response.json()
            assert data['test_id'] == 'vol_001_test'
            assert data['name'] == 'Test Volume Check'

    def test_get_test_not_found(self, app_client):
        """Test getting a non-existent test returns 404"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = None

            response = app_client.get("/v1/tests/nonexistent_test")

            assert response.status_code == 404
            assert "not found" in response.json()['detail']


class TestListTests:
    """Tests for GET /v1/tests endpoint"""

    def test_list_tests_all(self, app_client, sample_test_config):
        """Test listing all tests"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.list_tests.return_value = [sample_test_config]

            response = app_client.get("/v1/tests")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['test_id'] == 'vol_001_test'

    def test_list_tests_empty(self, app_client):
        """Test listing tests when none exist"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.list_tests.return_value = []

            response = app_client.get("/v1/tests")

            assert response.status_code == 200
            assert response.json() == []

    def test_list_tests_filter_enabled(self, app_client, sample_test_config):
        """Test filtering tests by enabled status"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.list_tests.return_value = [sample_test_config]

            response = app_client.get("/v1/tests?enabled=true")

            assert response.status_code == 200
            mock_db.list_tests.assert_called_with(enabled=True, test_type=None)

    def test_list_tests_filter_type(self, app_client, sample_test_config):
        """Test filtering tests by type"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.list_tests.return_value = [sample_test_config]

            response = app_client.get("/v1/tests?test_type=volume")

            assert response.status_code == 200
            mock_db.list_tests.assert_called_with(enabled=None, test_type='volume')


class TestUpdateTest:
    """Tests for PUT /v1/tests/{test_id} endpoint"""

    def test_update_test_success(self, app_client, sample_test_config):
        """Test successful test update"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = sample_test_config
            updated_config = {**sample_test_config, 'name': 'Updated Test Name'}
            mock_db.update_test.return_value = updated_config

            response = app_client.put(
                "/v1/tests/vol_001_test",
                json={'name': 'Updated Test Name'}
            )

            assert response.status_code == 200
            data = response.json()
            assert data['name'] == 'Updated Test Name'

    def test_update_test_not_found(self, app_client):
        """Test updating a non-existent test returns 404"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = None

            response = app_client.put(
                "/v1/tests/nonexistent_test",
                json={'name': 'Updated Name'}
            )

            assert response.status_code == 404


class TestDeleteTest:
    """Tests for DELETE /v1/tests/{test_id} endpoint"""

    def test_delete_test_success(self, app_client, sample_test_config):
        """Test successful test deletion (soft delete)"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = sample_test_config

            response = app_client.delete("/v1/tests/vol_001_test")

            assert response.status_code == 204
            mock_db.delete_test.assert_called_once_with('vol_001_test')

    def test_delete_test_not_found(self, app_client):
        """Test deleting a non-existent test returns 404"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = None

            response = app_client.delete("/v1/tests/nonexistent_test")

            assert response.status_code == 404


class TestTriggerTestExecution:
    """Tests for POST /v1/tests/{test_id}/run endpoint"""

    def test_trigger_execution_success(self, app_client, sample_test_config):
        """Test successful test execution trigger"""
        with patch('api.routers.tests.db_client') as mock_db, \
             patch('api.routers.tests.execute_test_task') as mock_task:
            mock_db.get_test.return_value = sample_test_config
            mock_task.delay.return_value = MagicMock(id='test-task-id-123')

            response = app_client.post(
                "/v1/tests/vol_001_test/run",
                json={'wait': False}
            )

            assert response.status_code == 202
            data = response.json()
            assert data['task_id'] == 'test-task-id-123'
            assert data['test_id'] == 'vol_001_test'
            assert data['status'] == 'queued'
            mock_task.delay.assert_called_once_with('vol_001_test')

    def test_trigger_execution_test_not_found(self, app_client):
        """Test triggering execution for non-existent test returns 404"""
        with patch('api.routers.tests.db_client') as mock_db:
            mock_db.get_test.return_value = None

            response = app_client.post(
                "/v1/tests/nonexistent_test/run",
                json={'wait': False}
            )

            assert response.status_code == 404
