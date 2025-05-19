import streamlit as st
import os
import datetime
from src.core.config import get_root_path, get_data_path
from src.core.helpers.video_helper import crop_video_files
from src.core.helpers.download_utils import filter_and_zip_files

# 导入共享组件
from src.ui.components.shared_styles import load_custom_css
from src.ui.components.file_manager import setup_working_directory

def show():
    """显示视频裁剪页面 / Display video crop page"""
    # 加载样式
    load_custom_css()
    
    # 页面标题和说明
    st.title("✂️ 视频裁剪 / Video Crop")
    
    with st.expander("💡 使用说明 / Instructions", expanded=True):
        st.markdown("""
        #### 视频要求 / Video Requirements:
        - 输入格式：MP4 / Input Format: MP4
        - 输出格式：MP4 / Output Format: MP4
        - 输出分辨率：500x500像素 / Output Resolution: 500x500 pixels
        - 输出帧率：与输入相同 / Output Frame Rate: Same as input
        """)
    
    # 设置路径和时间
    root_directory = os.path.join(get_data_path(), 'video_crop')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    web_log_file_path = os.path.join(get_root_path(), 'logs', 'usage.txt')
    
    tab1, tab2 = st.tabs([
        "✂️ 视频裁剪 / Video Crop",
        "📥 结果下载 / Download"
    ])
    
    with tab1:
        # 设置工作目录
        folder_path, selected_files = setup_working_directory(root_directory)
        
        if folder_path and selected_files:
            st.subheader("⚙️ 裁剪参数 / Crop Parameters")
            
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.number_input(
                    "开始时间（秒） / Start Time (seconds)",
                    min_value=0.0,
                    value=0.0,
                    help="设置裁剪的开始时间 / Set the start time for cropping"
                )
            
            with col2:
                duration = st.number_input(
                    "持续时间（秒） / Duration (seconds)",
                    min_value=0.1,
                    value=60.0,
                    help="设置裁剪的持续时间 / Set the duration for cropping"
                )
            
            if st.button("✂️ 开始裁剪 / Start Cropping", use_container_width=True):
                try:
                    with open(web_log_file_path, "a", encoding='utf-8') as web_log_file:
                        web_log_file.write(f"\n{st.session_state['name']}, {current_time}\n")
                    
                    with st.spinner("裁剪中 / Cropping..."):
                        crop_video_files(folder_path, selected_files, start_time, duration)
                    st.success("✅ 视频裁剪完成 / Video cropping completed")
                except Exception as e:
                    st.error(f"❌ 视频裁剪失败 / Video cropping failed: {e}")
        else:
            st.warning("⚠️ 请先选择工作目录和视频文件 / Please select working directory and video files first")
    
    with tab2:
        st.subheader("📥 结果下载 / Result Download")
        if folder_path:
            st.info(f"当前工作目录 / Current working folder: {os.path.basename(folder_path)}")
            
            try:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📦 下载所有文件 / Download All Files", use_container_width=True):
                        filter_and_zip_files(folder_path)
                
                with col2:
                    if st.button("📄 仅下载MP4文件 / Download Only MP4", use_container_width=True):
                        filter_and_zip_files(folder_path, included_ext=['.mp4'])
                
            except Exception as e:
                st.error(f"❌ 文件下载出错 / Error during file download: {e}")
        else:
            st.warning("⚠️ 请先在视频裁剪页面选择工作目录 / Please select a working directory in the video crop tab first")

if __name__ == "__main__":
    show() 