import os
import subprocess
import streamlit as st
import datetime
from typing import List, Dict, Optional

def create_and_start_analysis(folder_path: str, selected_files: list, config_path: str, gpu_count: int, current_time: str, selected_gpus: list = None) -> None:
    """创建并启动分析任务
    Create and start analysis task
    
    Args:
        folder_path (str): 工作目录路径
        selected_files (list): 选定的视频文件列表
        config_path (str): 模型配置文件路径
        gpu_count (int): GPU数量
        current_time (str): 当前时间
        selected_gpus (list): 选定的GPU列表
    """
    try:
        # 如果没有指定GPU，使用所有可用的GPU
        if selected_gpus is None:
            selected_gpus = list(range(gpu_count))

        st.write(f"调试信息 / Debug: {len(selected_files)} 个文件使用 {len(selected_gpus)} 个GPU")

        # 检查GPU数量和文件数量
        if len(selected_files) < len(selected_gpus):
            st.warning("文件数量少于GPU数量，部分GPU将不会被使用 / Not enough files for the number of GPUs. Some GPUs will not be used.")
            selected_gpus = selected_gpus[:len(selected_files)]

        # 计算每个GPU处理的文件数
        files_per_gpu = len(selected_files) // len(selected_gpus)
        remaining_files = len(selected_files) % len(selected_gpus)

        # 分配文件到不同的GPU
        file_groups = []
        start = 0
        processes = []  # 记录每个GPU的子进程

        # 将文件分组
        for i in range(len(selected_gpus)):
            end = start + files_per_gpu + (1 if i < remaining_files else 0)
            file_groups.append(selected_files[start:end])
            start = end

        # 为每个GPU组创建和执行脚本
        for group_num, files_group in enumerate(file_groups):
            if not files_group:
                continue

            gpu_index = selected_gpus[group_num]
            run_py_path = os.path.join(folder_path, f'run_gpu{gpu_index}.py')
            start_script_path = os.path.join(folder_path, f'start_analysis_gpu{gpu_index}.py')
            log_file_path = os.path.join(folder_path, f'output_gpu{gpu_index}.log')

            # 创建运行脚本内容
            analyze_videos_code = f"deeplabcut.analyze_videos(r'{config_path}', {files_group}, videotype='mp4', shuffle=1, trainingsetindex=0, gputouse={gpu_index}, save_as_csv=True)"
            create_labeled_video_code = f"deeplabcut.create_labeled_video(r'{config_path}', {files_group})"

            content = f"""
import deeplabcut

{analyze_videos_code}

{create_labeled_video_code}
"""
            # 写入运行脚本
            with open(run_py_path, 'w', encoding='utf-8') as file:
                file.write(content)

            # 创建启动脚本内容
            start_content = f"""
import subprocess

subprocess.run(['python', r'{run_py_path}'], check=True)
"""
            # 写入启动脚本
            with open(start_script_path, 'w', encoding='utf-8') as file:
                file.write(start_content)

            # 启动分析进程
            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                process = subprocess.Popen(
                    ['python', start_script_path],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=folder_path
                )
                processes.append((process, gpu_index))

            st.success(f"✅ 已在GPU {gpu_index}上启动分析任务 / Analysis task started on GPU {gpu_index}")

        # 等待所有进程完成
        for process, gpu_index in processes:
            process.wait()
            if process.returncode != 0:
                st.error(f"❌ GPU {gpu_index}上的分析任务出错 / Error encountered while running analysis on GPU {gpu_index}")

        # 记录到总日志文件
        general_log_path = os.path.join(folder_path, 'general_log.txt')
        with open(general_log_path, 'a', encoding='utf-8') as general_log:
            for _, gpu_index in processes:
                general_log.write(f'[{current_time}] 在GPU {gpu_index}上启动了分析 / Analysis started on GPU {gpu_index}\n')

    except Exception as e:
        st.error(f"❌ 创建分析任务失败 / Failed to create analysis task: {str(e)}")
        raise e

def fetch_last_lines_of_logs(folder_path: str, gpu_count: int = 1, num_lines: int = 20) -> dict:
    """获取日志文件的最后几行
    Get the last few lines of log files
    
    Args:
        folder_path (str): 日志文件所在目录
        gpu_count (int): GPU数量
        num_lines (int): 要获取的行数
        
    Returns:
        dict: 包含日志文件名和内容的字典
    """
    last_lines = {}
    encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
    
    for group_num in range(gpu_count):
        log_file_path = os.path.join(folder_path, f'output_gpu{group_num}.log')
        content = f"未找到日志文件 / Log file not found: {log_file_path}"
        
        if os.path.exists(log_file_path):
            for encoding in encodings:
                try:
                    with open(log_file_path, 'r', encoding=encoding) as log_file:
                        lines = log_file.readlines()
                        if lines:
                            # 获取最后num_lines行
                            content = ''.join(lines[-num_lines:])
                        else:
                            content = "没有日志记录 / No entries in log."
                    break  # 如果成功读取，跳出编码尝试循环
                except UnicodeDecodeError:
                    continue  # 如果当前编码失败，尝试下一个编码
                except Exception as e:
                    content = f"读取日志文件时出错 / Error reading log file: {str(e)}"
                    break
        
        last_lines[f'GPU{group_num} 日志 / Log'] = content
    
    return last_lines 