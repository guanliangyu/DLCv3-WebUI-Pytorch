import os
import pandas as pd
import numpy as np
import streamlit as st

def process_mouse_scratch_video(file_path, folder_path, paw_probability_threshold=0.99999, min_distance=10, max_distance=25):
    """处理小鼠抓挠视频的分析结果
    Process mouse scratch video analysis results
    
    Args:
        file_path (str): CSV文件路径
        folder_path (str): 输出文件夹路径
        paw_probability_threshold (float): 爪子位置概率阈值
        min_distance (float): 最小移动距离
        max_distance (float): 最大移动距离
    """
    try:
        # 读取CSV文件，跳过前三行
        data = pd.read_csv(file_path, skiprows=3, header=None)
        
        if data.empty:
            st.warning(f"文件中没有数据 / No data in file: {file_path}")
            return None
            
        # 计算爪子在连续帧之间的移动距离
        data[4] = np.sqrt((data[1].diff() ** 2) + (data[2].diff() ** 2))
        data[4].iloc[0] = 0  # 设置第一行的距离为0
        
        # 计算每帧的时间（分钟）
        data[5] = data[0] / (30 * 60)  # 30帧/秒
        
        # 根据爪子位置概率过滤数据
        data = data[data[3] >= paw_probability_threshold]
        
        # 根据移动距离过滤数据
        data = data[(data[4] >= min_distance) & (data[4] <= max_distance)]
        
        if data.empty:
            st.warning(f"过滤后没有有效数据 / No valid data after filtering: {file_path}")
            return None
            
        # 保存过滤后的数据
        base_file_name = os.path.splitext(os.path.basename(file_path))[0]
        filtered_file_path = os.path.join(folder_path, f"{base_file_name}_filtered.csv")
        data.to_csv(filtered_file_path, index=False, header=False)
        
        try:
            data[5] = data[5].astype(int)
        except ValueError as e:
            st.error(f"时间转换错误 / Error converting time: {str(e)}")
            return None
            
        # 计算每分钟的得分
        scores_per_minute = data.groupby(data[5].astype(int))[0].count().reindex(
            range(int(data[5].max()) + 1), 
            fill_value=0
        )
        scores_per_minute_file_path = os.path.join(folder_path, f"{base_file_name}_filtered_min.csv")
        scores_per_minute.to_csv(scores_per_minute_file_path, header=False)
        
        # 修改每分钟得分，计数<=5的设为0
        scores_per_minute[scores_per_minute <= 5] = 0
        
        # 计算5分钟间隔的得分总和
        scores_5min_intervals = scores_per_minute.groupby(scores_per_minute.index // 5).sum()
        scores_5min_intervals_file_path = os.path.join(folder_path, f"{base_file_name}_filtered_5min_intervals.csv")
        scores_5min_intervals.to_csv(scores_5min_intervals_file_path, header=False)
        
        st.success(f"✅ 处理完成 / Processing completed: {os.path.basename(file_path)}")
        return (paw_probability_threshold, min_distance, max_distance, 
                filtered_file_path, scores_per_minute_file_path, scores_5min_intervals_file_path)
                
    except Exception as e:
        st.error(f"处理文件失败 / Failed to process file: {str(e)}")
        return None

def process_scratch_files(folder_path, paw_probability_threshold=0.99999, min_distance=10, max_distance=25):
    """处理文件夹中的所有抓挠视频分析结果
    Process all scratch video analysis results in the folder
    
    Args:
        folder_path (str): 文件夹路径
        paw_probability_threshold (float): 爪子位置概率阈值
        min_distance (float): 最小移动距离
        max_distance (float): 最大移动距离
    """
    try:
        # 查找所有以"00000.csv"结尾的文件
        file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                     if f.endswith("00000.csv")]
        
        if not file_paths:
            st.warning("未找到分析结果文件 / No analysis result files found")
            return
            
        # 处理每个文件
        processed_files_list = []
        for file_path in file_paths:
            result = process_mouse_scratch_video(
                file_path, 
                folder_path, 
                paw_probability_threshold, 
                min_distance, 
                max_distance
            )
            if result:
                processed_files_list.append(result)
                
        # 显示处理结果
        if processed_files_list:
            st.success(f"✅ 成功处理 {len(processed_files_list)} 个文件 / Successfully processed {len(processed_files_list)} files")
            for result in processed_files_list:
                st.write(result)
        else:
            st.warning("没有成功处理的文件 / No files were successfully processed")
            
    except Exception as e:
        st.error(f"处理文件夹失败 / Failed to process folder: {str(e)}") 