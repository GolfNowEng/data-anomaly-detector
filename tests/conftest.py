"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient
import sys

# Mock pyodbc at module level to prevent import errors
sys.modules['pyodbc'] = MagicMock()


@pytest.fixture
def sample_test_config():
    """Sample test configuration for testing"""
    return {
        'test_id': 'vol_001_test',
        'name': 'Test Volume Check',
        'description': 'Test description',
        'test_type': 'volume',
        'enabled': True,
        'severity': 'high',
        'connection_id': 'test_connection',
        'query': 'SELECT COUNT(*) as count FROM test_table',
        'parameters': {
            'anomaly_threshold_min': 100,
            'alert_on_empty': True
        },
        'tags': ['test', 'volume'],
        'notification_config': {
            'on_failure': ['email'],
            'recipients': ['test@example.com']
        },
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'created_by': 'system',
        'updated_by': 'system'
    }


@pytest.fixture
def sample_connection_config():
    """Sample connection configuration for testing"""
    return {
        'connection_id': 'test_connection',
        'name': 'Test Database',
        'db_type': 'postgres',
        'host': 'localhost',
        'port': 5432,
        'database_name': 'test_db',
        'username': 'test_user',
        'password': 'test_password',
        'environment': 'development'
    }


@pytest.fixture
def app_client():
    """FastAPI test client"""
    from api.main import app
    with TestClient(app) as client:
        yield client
