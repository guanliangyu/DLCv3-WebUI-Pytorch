import streamlit as st
import os
import datetime
from src.core.config import get_root_path, get_data_path
from src.core.helpers.video_helper import process_video_files, merge_videos
from src.core.helpers.download_utils import filter_and_zip_files

# 导入共享组件
from src.ui.components.shared_styles import load_custom_css
from src.ui.components.file_manager import setup_working_directory

def show():
    """显示视频预处理页面 / Display video preparation page"""
    # 加载样式
    load_custom_css()
    
    # 页面标题和说明
    st.title("📽️ 视频预处理 / Video Preparation")
    
    with st.expander("💡 使用说明 / Instructions", expanded=True):
        st.markdown("""
        #### 视频要求 / Video Requirements:
        - 输入格式：任意视频格式 / Input Format: Any video format
        - 输出格式：MP4 / Output Format: MP4
        - 输出分辨率：500x500像素 / Output Resolution: 500x500 pixels
        - 输出帧率：30帧/秒 / Output Frame Rate: 30 fps
        """)
    
    # 设置路径和时间
    root_directory = os.path.join(get_data_path(), 'video_prepare')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    web_log_file_path = os.path.join(get_root_path(), 'logs', 'usage.txt')
    
    tab1, tab2, tab3 = st.tabs([
        "🎬 视频处理 / Video Processing",
        "🔄 视频合并 / Video Merge",
        "📥 结果下载 / Download"
    ])
    
    with tab1:
        # 设置工作目录
        folder_path, selected_files = setup_working_directory(root_directory)
        
        if folder_path and selected_files:
            st.subheader("⚙️ 处理参数 / Processing Parameters")
            
            col1, col2 = st.columns(2)
            with col1:
                target_fps = st.number_input(
                    "目标帧率 / Target FPS",
                    min_value=1,
                    max_value=60,
                    value=30,
                    help="设置输出视频的帧率 / Set the frame rate of output video"
                )
            
            with col2:
                target_size = st.number_input(
                    "目标尺寸 / Target Size",
                    min_value=100,
                    max_value=1000,
                    value=500,
                    help="设置输出视频的尺寸（像素） / Set the size of output video (pixels)"
                )
            
            if st.button("🚀 开始处理 / Start Processing", use_container_width=True):
                try:
                    with open(web_log_file_path, "a", encoding='utf-8') as web_log_file:
                        web_log_file.write(f"\n{st.session_state['name']}, {current_time}\n")
                    
                    with st.spinner("处理中 / Processing..."):
                        process_video_files(folder_path, selected_files, target_fps, target_size)
                    st.success("✅ 视频处理完成 / Video processing completed")
                except Exception as e:
                    st.error(f"❌ 视频处理失败 / Video processing failed: {e}")
        else:
            st.warning("⚠️ 请先选择工作目录和视频文件 / Please select working directory and video files first")
    
    with tab2:
        st.subheader("🔄 视频合并 / Video Merge")
        if folder_path:
            st.info(f"当前工作目录 / Current working folder: {os.path.basename(folder_path)}")
            
            # 选择要合并的视频
            st.subheader("📁 选择视频 / Select Videos")
            video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
            selected_videos = st.multiselect(
                "选择要合并的视频 / Select videos to merge",
                video_files,
                help="按照所需顺序选择视频 / Select videos in desired order"
            )
            
            if selected_videos:
                output_name = st.text_input(
                    "输出文件名 / Output filename",
                    value="merged_video.mp4",
                    help="设置合并后的视频文件名 / Set the filename for merged video"
                )
                
                if st.button("🔄 合并视频 / Merge Videos", use_container_width=True):
                    try:
                        with st.spinner("合并中 / Merging..."):
                            video_paths = [os.path.join(folder_path, video) for video in selected_videos]
                            output_path = os.path.join(folder_path, output_name)
                            merge_videos(video_paths, output_path)
                        st.success("✅ 视频合并完成 / Video merge completed")
                    except Exception as e:
                        st.error(f"❌ 视频合并失败 / Video merge failed: {e}")
            else:
                st.warning("⚠️ 请选择要合并的视频 / Please select videos to merge")
        else:
            st.warning("⚠️ 请先在视频处理页面选择工作目录 / Please select a working directory in the video processing tab first")
    
    with tab3:
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
            st.warning("⚠️ 请先在视频处理页面选择工作目录 / Please select a working directory in the video processing tab first")

if __name__ == "__main__":
    show() 