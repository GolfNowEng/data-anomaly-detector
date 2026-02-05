"""
Tests for VolumeTestExecutor
"""
import pytest
from unittest.mock import MagicMock, patch


class TestVolumeTestExecutor:
    """Tests for VolumeTestExecutor class"""

    @pytest.fixture
    def executor(self):
        """Create VolumeTestExecutor instance"""
        from workers.executors.volume_test import VolumeTestExecutor
        return VolumeTestExecutor()

    @pytest.fixture
    def mock_connector(self):
        """Create mock database connector"""
        connector = MagicMock()
        connector.__enter__ = MagicMock(return_value=connector)
        connector.__exit__ = MagicMock(return_value=None)
        return connector

    def test_execute_volume_test_passes_above_threshold(self, executor, mock_connector):
        """Test volume test passes when count is above threshold"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {
                'anomaly_threshold_min': 100,
                'alert_on_empty': True
            }
        }

        mock_connector.execute_query.return_value = [{'count': 500}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'passed'
        assert result['actual']['count'] == 500
        assert result['summary']['is_anomaly'] is False

    def test_execute_volume_test_fails_below_threshold(self, executor, mock_connector):
        """Test volume test fails when count is below threshold"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {
                'anomaly_threshold_min': 100,
                'alert_on_empty': True
            }
        }

        mock_connector.execute_query.return_value = [{'count': 50}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'failed'
        assert result['actual']['count'] == 50
        assert result['summary']['is_anomaly'] is True
        assert 'below minimum threshold' in result['summary']['reason']

    def test_execute_volume_test_fails_on_empty_table(self, executor, mock_connector):
        """Test volume test fails when table is empty and alert_on_empty is True"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {
                'anomaly_threshold_min': 100,
                'alert_on_empty': True
            }
        }

        mock_connector.execute_query.return_value = [{'count': 0}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'failed'
        assert result['summary']['is_anomaly'] is True
        assert result['summary']['reason'] == 'Table is empty'

    def test_execute_volume_test_passes_on_empty_when_not_alerting(self, executor, mock_connector):
        """Test volume test passes on empty table when alert_on_empty is False"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {
                'anomaly_threshold_min': None,  # No minimum threshold
                'alert_on_empty': False
            }
        }

        mock_connector.execute_query.return_value = [{'count': 0}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'passed'
        assert result['summary']['is_anomaly'] is False

    def test_execute_volume_test_handles_no_results(self, executor, mock_connector):
        """Test volume test handles query returning no results"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {}
        }

        mock_connector.execute_query.return_value = []

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'failed'
        assert 'Query returned no results' in result['summary']['error']

    def test_execute_volume_test_detects_count_column_variations(self, executor, mock_connector):
        """Test volume test correctly identifies different count column names"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as total FROM test_table',
            'parameters': {
                'anomaly_threshold_min': 100
            }
        }

        # Result uses 'total' instead of 'count'
        mock_connector.execute_query.return_value = [{'total': 500}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'passed'
        assert result['actual']['count'] == 500

    def test_execute_volume_test_uses_explicit_count_column(self, executor, mock_connector):
        """Test volume test uses explicitly specified count column"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT custom_count FROM test_table',
            'parameters': {
                'count_column': 'custom_count',
                'anomaly_threshold_min': 100
            }
        }

        mock_connector.execute_query.return_value = [{'custom_count': 500}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'passed'
        assert result['actual']['count'] == 500

    def test_execute_volume_test_handles_database_error(self, executor, mock_connector):
        """Test volume test handles database connection errors"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {}
        }

        mock_connector.execute_query.side_effect = Exception("Database connection failed")

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'error'
        assert 'Database connection failed' in result['error_message']

    def test_execute_volume_test_no_threshold_always_passes(self, executor, mock_connector):
        """Test volume test passes when no threshold is configured"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {
                'anomaly_threshold_min': None,
                'alert_on_empty': False
            }
        }

        mock_connector.execute_query.return_value = [{'count': 1}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        assert result['status'] == 'passed'
        assert result['summary']['is_anomaly'] is False

    def test_execute_volume_test_result_structure(self, executor, mock_connector):
        """Test volume test result has correct structure"""
        test_config = {
            'test_id': 'vol_001_test',
            'connection_id': 'test_conn',
            'query': 'SELECT COUNT(*) as count FROM test_table',
            'parameters': {
                'anomaly_threshold_min': 100
            }
        }

        mock_connector.execute_query.return_value = [{'count': 500}]

        with patch('workers.executors.volume_test.get_connector', return_value=mock_connector):
            result = executor.execute(test_config)

        # Verify result structure
        assert 'status' in result
        assert 'summary' in result
        assert 'actual' in result
        assert 'expected' in result
        assert 'rows_processed' in result

        # Verify summary structure
        assert 'count' in result['summary']
        assert 'threshold_min' in result['summary']
        assert 'is_anomaly' in result['summary']
