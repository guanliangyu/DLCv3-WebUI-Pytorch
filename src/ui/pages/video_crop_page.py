import streamlit as st
import os
import datetime
import cv2
import subprocess
import shutil


# Data handling
import pandas as pd
import numpy as np

# Utilization and helpers
from src.core.config import get_root_path
from src.core.utils.gpu_utils import display_gpu_usage
from src.core.utils.gpu_selector import setup_gpu_selection
from src.core.utils.file_utils import create_new_folder, upload_files, list_directories, display_folder_contents, create_folder_if_not_exists, select_video_files, select_python_files
from src.core.utils.execute_selected_scripts import execute_selected_scripts, fetch_last_lines_of_logs

from src.core.helpers.video_combiner import create_video_combination_script



# File processing
from src.core.processing.mouse_scratch_video_processing import process_mouse_scratch_video, process_scratch_files


def extract_specific_frames(video_path):
    """Extracts the first, middle, and last frames of a video."""
    import cv2
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    
    for count in [0, frame_count // 2, frame_count - 1]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, count)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames
    
def display_frames(frames):
    """Displays frames side by side in Streamlit."""
    cols = st.columns(len(frames))
    for col, frame in zip(cols, frames):
        col.image(frame, channels="BGR", use_column_width=True)

def show_cropped_frame(frame_path, x, y, width, height):
    if frame_path is not None:
        # Load the first frame
        frame = cv2.imread(frame_path)
        if frame is not None:
            # Crop the image based on the input parameters
            crop_img = frame[y:y+height, x:x+width]
            # Convert the cropped image from BGR to RGB (OpenCV to normal image format)
            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
            # Display the cropped frame in the Streamlit UI
            st.image(crop_img, caption='Cropped Frame', use_column_width=True)
        else:
            st.error("Failed to load the saved frame for cropping.")
    else:
        st.error("No frame has been saved yet to show.")

def create_extract_script(video_path, x, y, width, height, start, end, output_directory, deviceID=0):
    """
    Generates a Python script to crop and extract a segment of a video using ffmpeg, specifying a GPU device.

    Args:
    video_path (str): Path to the input video file.
    x (int): The x-coordinate for the crop operation.
    y (int): The y-coordinate for the crop operation.
    width (int): Width of the crop.
    height (int): Height of the crop.
    start (float): Start time in minutes for the video segment.
    end (float): End time in minutes for the video segment.
    output_directory (str): Directory to save the output file and script.
    deviceID (int): GPU device ID to use for processing.

    Returns:
    str: The path to the generated Python script.
    """
    # Calculate the start time and duration from input minutes
    start_time = str(datetime.timedelta(minutes=start))  # Converts to 'HH:MM:SS' format
    duration = str(datetime.timedelta(minutes=(end - start)))  # Converts to 'HH:MM:SS' format

    # Extract the base name of the video file without the extension
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]

    # Define the output filename incorporating video base name, x, and y coordinates
    output_filename = f'{video_base_name}_{x}_{y}_{start}_{end}.mp4'

    # Construct the output file path
    output_full_path = os.path.join(output_directory, output_filename)

    # Define the Python script filename based on the video file name and coordinates
    script_filename = f"{video_base_name}_{x}_{y}_{start}_{end}.py"
    script_path = os.path.join(output_directory, script_filename)

    # Write the Python script
    with open(script_path, 'w') as f:
        f.write('import subprocess\n')
        # Construct the ffmpeg command using hardware acceleration and specific codecs
        command = f"""subprocess.run('ffmpeg -hwaccel cuda -hwaccel_device {deviceID} -c:v h264_cuvid -ss "{start_time}" -t "{duration}" -i "{video_path}" -vf "crop={width}:{height}:{x}:{y},fps=30" -c:v h264_nvenc -gpu {deviceID} -an "{output_full_path}"', shell=True)"""
        f.write(command + '\n')

    return script_path

def create_extract_script_CPU(video_path, x, y, width, height, start, end, output_directory, deviceID=0):
    # Calculate the start time and duration from input minutes
    start_time = str(datetime.timedelta(minutes=start))  # Converts to 'HH:MM:SS' format
    duration = str(datetime.timedelta(minutes=(end - start)))  # Converts to 'HH:MM:SS' format

    # Extract the base name of the video file without the extension
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]

    # Define the output filename incorporating video base name, x, and y coordinates
    output_filename = f'{video_base_name}_{x}_{y}_{start}_{end}.mp4'

    # Construct the output file path
    output_full_path = os.path.join(output_directory, output_filename)

    # Define the Python script filename based on the video file name and coordinates
    script_filename = f"{video_base_name}_{x}_{y}_{start}_{end}.py"
    script_path = os.path.join(output_directory, script_filename)

    # Write the Python script
    with open(script_path, 'w') as f:
        f.write('import subprocess\n')
        # Construct the ffmpeg command using hardware acceleration and specific codecs
        command = f"""subprocess.run('ffmpeg -hwaccel cuda -hwaccel_device {deviceID} -ss "{start_time}" -t "{duration}" -i "{video_path}" -vf "crop={width}:{height}:{x}:{y},fps=30" -c:v h264_nvenc -an "{output_full_path}"', shell=True)"""
        f.write(command + '\n')

    return script_path

def move_selected_files(dest_folder_path, selected_files, combined_video_path):
    """
    Moves selected files from a combined video path to a specified destination directory.

    Args:
    dest_folder_path (str): The full path of the directory to move files into.
    selected_files (list): List of filenames selected for moving.
    combined_video_path (str): The path where combined videos are currently stored.
    """
    if not os.path.exists(dest_folder_path):
        os.makedirs(dest_folder_path)
        st.success(f"Created directory: {dest_folder_path}")
    else:
        st.success(f"Directory already exists: {dest_folder_path}")

    # Move the selected files
    files_moved = 0
    for filename in selected_files:
        src_path = os.path.join(combined_video_path, filename)
        dest_path = os.path.join(dest_folder_path, filename)
        shutil.move(src_path, dest_path)
        files_moved += 1

    if files_moved > 0:
        st.success(f"Moved {files_moved} files to {dest_folder_path}")
    else:
        st.info("No files selected to move.")

def video_crop_page():
    root_directory = os.path.join(get_root_path(), 'video_prepare')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(root_directory, folder_name)
    web_log_file_path = os.path.join(get_root_path(), 'streamlit', 'log', 'usage.txt')
    
    # 页面标题和说明
    st.title("✂️ 视频剪辑工具 / Video Crop Tool")
    
    with st.expander("💡 使用说明 / Instructions", expanded=True):
        st.markdown("""
        #### 视频要求 / Video Requirements:
        - 格式为MP4 / Format: MP4
        - 已完成视频拼接 / Completed video preparation
        
        #### 剪辑参数说明 / Crop Parameters:
        - X, Y: 剪辑起始坐标 / Starting coordinates
        - 宽度, 高度: 剪辑区域大小 / Crop area size
        - 开始时间, 结束时间: 视频片段时间范围（分钟）/ Video segment time range (minutes)
        
        #### GPU使用提示 / GPU Usage Note:
        - 如果GPU显存占用率很高，说明其他用户正在使用  
          If GPU memory usage is high, other users are currently using it
        - 请等待GPU资源释放后再开始新的工作  
          Please wait until GPU resources are available before starting new work
        """)
    
    # GPU状态显示
    st.subheader("🖥️ GPU 状态 / GPU Status")
    high_memory_usage = display_gpu_usage()

    # GPU配置
    st.subheader("⚙️ GPU 配置 / GPU Configuration")
    gpu_count, selected_gpus = setup_gpu_selection()
    if selected_gpus:
        st.success(f"可用GPU数量 / Available GPUs: {gpu_count}")
        st.info(f"已选择的GPU / Selected GPUs: {selected_gpus}")
    
    # 目录选择
    st.subheader("📁 工作目录 / Working Directory")
    directories = list_directories(root_directory)
    if directories:
        selected_directory = st.selectbox("📂 选择工作目录 / Choose a directory", directories)
        folder_path = os.path.join(root_directory, selected_directory, 'combined-video')
        st.success(f"当前工作目录 / Current working folder: {folder_path}")
    else:
        st.error("⚠️ 未找到工作目录 / No directories found")
        return

    # 视频选择和预览
    combined_video_path = folder_path
    create_folder_if_not_exists(folder_path)
    
    with st.container():
        st.subheader("📤 文件上传 / File Upload")
        upload_files(folder_path)
    
    # 视频文件列表
    video_files = [file for file in os.listdir(combined_video_path) if file.lower().endswith('.mp4')]
    if video_files:
        st.subheader("🎥 视频预览 / Video Preview")
        selected_video = st.selectbox("选择要处理的视频 / Select a video to process", video_files, key='video_select')
        video_path = os.path.join(combined_video_path, selected_video)
        
        frames = extract_specific_frames(video_path)
        if frames:
            st.markdown("#### 视频帧预览 / Frame Preview")
            cols = st.columns(len(frames))
            for i, (col, frame) in enumerate(zip(cols, frames)):
                col.image(frame, channels="BGR", use_column_width=True, caption=f"Frame {i+1}")
        
        # 剪辑参数设置
        st.subheader("✂️ 剪辑参数 / Crop Parameters")
        
        # 位置和大小设置
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            x = st.number_input("X坐标 / X Position:", min_value=0, value=100, key="x_pos")
        with col2:
            y = st.number_input("Y坐标 / Y Position:", min_value=0, value=100, key="y_pos")
        with col3:
            width = st.number_input("宽度 / Width:", min_value=1, value=500, key="width")
        with col4:
            height = st.number_input("高度 / Height:", min_value=1, value=500, key="height")

        # 时间范围设置
        col5, col6 = st.columns(2)
        with col5:
            start = st.number_input("开始时间(分钟) / Start Time (min):", min_value=0, value=0, step=1, key="start_time")
        with col6:
            end = st.number_input("结束时间(分钟) / End Time (min):", min_value=0, value=1, step=1, key="end_time")
        
        # 预览剪辑效果
        if st.button("👁️ 预览剪辑效果 / Preview Crop", key="preview_button"):
            st.markdown("#### 剪辑预览 / Crop Preview")
            cropped_frames = [frame[y:y+height, x:x+width] for frame in frames]
            cols = st.columns(len(cropped_frames))
            for i, (col, frame) in enumerate(zip(cols, cropped_frames)):
                col.image(frame, channels="BGR", use_column_width=True, caption=f"Cropped Frame {i+1}")

        # GPU检查
        if not selected_gpus:
            st.error("❌ 未选择GPU或无可用GPU / No GPUs selected or available")
            return
        
        # 初始化GPU循环索引
        if 'current_gpu_index' not in st.session_state:
            st.session_state['current_gpu_index'] = 0
        
        # 生成脚本按钮
        st.subheader("🚀 生成处理脚本 / Generate Scripts")
        col7, col8 = st.columns(2)
        with col7:
            if st.button("💾 生成H.264视频处理脚本 / Create H.264 Video Script"):
                deviceID = selected_gpus[st.session_state['current_gpu_index']]
                script_name = create_extract_script(video_path, x, y, width, height, start, end, combined_video_path, deviceID)
                st.success(f"✅ 脚本生成成功 / Script generated: {script_name}")
                st.session_state['current_gpu_index'] = (st.session_state['current_gpu_index'] + 1) % len(selected_gpus)

        with col8:
            if st.button("💻 生成CPU处理脚本(非H.264视频) / Create CPU Script (Non-H.264)"):
                script_name = create_extract_script_CPU(video_path, x, y, width, height, start, end, combined_video_path)
                st.success(f"✅ 脚本生成成功 / Script generated: {script_name}")
    else:
        st.warning("📭 未找到视频文件 / No video files found")

    # Script execution part
    st.subheader("🚀 执行处理脚本 / Execute Scripts")
    
    # 从combined_video_path中选择Python脚本
    python_files = select_python_files(combined_video_path)
    
    if python_files:
        if st.button("▶️ 执行选中的脚本 / Execute Selected Scripts", key='execute_scripts'):
            try:
                output_directory = combined_video_path
                log_files = execute_selected_scripts(folder_path, python_files, output_directory, execute=True)
                st.session_state['log_files'] = log_files
                st.success("✅ 脚本正在执行 / Scripts are being executed")
            except subprocess.CalledProcessError as e:
                st.error(f"❌ 脚本执行失败 / Failed to execute scripts: {str(e)}")
    else:
        st.info("📝 未选择Python脚本 / No Python scripts selected")

    st.subheader("📁 文件管理 / File Management")

    st.write("Check and manage directories:")

    # List all files that meet the criteria from combined_video_path
    video_files = [f for f in os.listdir(combined_video_path) if '_' in f and f.lower().endswith('.mp4')]
    selected_files = st.multiselect('选择要移动的视频文件 / Select video files to move:', video_files, key="file_selector")

    st.write("移动选中的文件到: / Move Selected Files to:")
    col9, col10, col11, col12, col13, col14 = st.columns(6)
    root_path = get_root_path()
    with col9:
        if st.button('Scratch', key="move_to_scratch"):
            dest_folder_path = os.path.join(root_path, 'Scratch/', selected_directory)
            move_selected_files(dest_folder_path, selected_files, combined_video_path)
    with col10:
        if st.button('Grooming', key="move_to_grooming"):
            dest_folder_path = os.path.join(root_path, 'Grooming/', selected_directory)
            move_selected_files(dest_folder_path, selected_files, combined_video_path)
    with col11:
        if st.button('Three-Chamber', key="move_to_three_chamber"):
            dest_folder_path = os.path.join(root_path, 'Three-Chamber/', selected_directory)
            move_selected_files(dest_folder_path, selected_files, combined_video_path)
    with col12:
        if st.button('Two-Saver', key="move_to_two_saver"):
            dest_folder_path = os.path.join(root_path, 'Two-Saver/', selected_directory)
            move_selected_files(dest_folder_path, selected_files, combined_video_path)
    with col13:
        if st.button('CPP', key="move_to_cpp"):
            dest_folder_path = os.path.join(root_path, 'CPP/', selected_directory)
            move_selected_files(dest_folder_path, selected_files, combined_video_path)
    with col14:
        if st.button('Swimming', key="move_to_swimming"):
            dest_folder_path = os.path.join(root_path, 'Swimming/', selected_directory)
            move_selected_files(dest_folder_path, selected_files, combined_video_path)

    # Log file display button
    if st.button("显示最新日志 / Show Last Log Lines", key='show_logs'):
        last_lines = fetch_last_lines_of_logs(combined_video_path)
        if last_lines:
            for file, line in last_lines.items():
                st.text(f"{file}: {line}")
        else:
            st.error("No log files found in the directory.")

if __name__ == "__main__":
    video_crop_page()
