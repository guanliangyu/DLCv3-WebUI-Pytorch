import pytest
from unittest.mock import patch, MagicMock
from src.core.gpu.gpu_utils import get_gpu_utilization, display_gpu_usage

def test_get_gpu_utilization_no_gpus():
    with patch('GPUtil.getGPUs', return_value=[]):
        result = get_gpu_utilization()
        assert result == []

def test_get_gpu_utilization_with_gpus():
    mock_gpu = MagicMock()
    mock_gpu.memoryUtil = 0.5
    mock_gpu.load = 0.7
    mock_gpu.id = 0
    mock_gpu.memoryTotal = 8192
    mock_gpu.memoryUsed = 4096
    
    with patch('GPUtil.getGPUs', return_value=[mock_gpu]):
        result = get_gpu_utilization()
        assert len(result) == 1
        assert result[0]['id'] == 0
        assert result[0]['memory_util'] == 0.5
        assert result[0]['gpu_util'] == 0.7
        assert result[0]['total_memory'] == 8192
        assert result[0]['used_memory'] == 4096

def test_display_gpu_usage(capsys):
    mock_gpu = MagicMock()
    mock_gpu.memoryUtil = 0.8  # 80% memory utilization
    mock_gpu.load = 0.6  # 60% GPU utilization
    mock_gpu.id = 0
    mock_gpu.memoryTotal = 8192
    mock_gpu.memoryUsed = 6554
    
    with patch('GPUtil.getGPUs', return_value=[mock_gpu]):
        high_memory = display_gpu_usage()
        assert high_memory  # Should return True as memory utilization > 75%

def test_display_gpu_usage_low_memory(capsys):
    mock_gpu = MagicMock()
    mock_gpu.memoryUtil = 0.5  # 50% memory utilization
    mock_gpu.load = 0.3  # 30% GPU utilization
    mock_gpu.id = 0
    mock_gpu.memoryTotal = 8192
    mock_gpu.memoryUsed = 4096
    
    with patch('GPUtil.getGPUs', return_value=[mock_gpu]):
        high_memory = display_gpu_usage()
        assert not high_memory  # Should return False as memory utilization < 75% 