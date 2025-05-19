import GPUtil
from typing import List, Dict

def get_gpu_utilization() -> List[Dict]:
    """
    获取所有GPU的使用情况
    Get utilization of all GPUs
    
    Returns:
        List[Dict]: GPU使用情况列表，每个字典包含GPU ID、内存使用率和GPU使用率
    """
    gpus = GPUtil.getGPUs()
    return [{
        'id': gpu.id,
        'memory_util': gpu.memoryUtil,
        'gpu_util': gpu.load,
        'total_memory': gpu.memoryTotal,
        'used_memory': gpu.memoryUsed
    } for gpu in gpus] 