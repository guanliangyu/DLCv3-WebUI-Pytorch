import os
from typing import Dict, List

def sort_files_by_extension(folder_path: str) -> Dict[str, List[str]]:
    """
    按扩展名对目录中的文件进行排序
    Sort files in directory by extension
    
    Args:
        folder_path (str): 目录路径
        
    Returns:
        Dict[str, List[str]]: 按扩展名分组的文件字典
    """
    files_dict = {}
    for file in os.listdir(folder_path):
        ext = os.path.splitext(file)[1]
        if ext not in files_dict:
            files_dict[ext] = []
        files_dict[ext].append(file)
    return files_dict 