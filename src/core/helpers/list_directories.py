import os
from typing import List

def list_directories(root_path: str) -> List[str]:
    """
    列出指定目录下的所有子目录
    List all subdirectories in the specified directory
    
    Args:
        root_path (str): 根目录路径
        
    Returns:
        List[str]: 子目录列表
    """
    return [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))] 