import streamlit as st
import os
import datetime

# 导入配置和工具
from src.core.config import get_root_path, get_data_path, get_models_path

from src.core.utils.gpu_utils import display_gpu_usage
from src.core.utils.gpu_selector import setup_gpu_selection
from src.core.utils.file_utils import create_new_folder, upload_files, list_directories, display_folder_contents, create_folder_if_not_exists, select_video_files

from src.core.helpers.analysis_helper import create_and_start_analysis, fetch_last_lines_of_logs
from src.core.helpers.download_utils import create_download_button, filter_and_zip_files

# 导入处理模块
from src.core.processing.mouse_swimming_video_processing import process_mouse_swimming_video, process_swimming_files

def mouse_swimming_page():
    root_directory = os.path.join(get_data_path(), 'swimming')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(root_directory, folder_name)
    web_log_file_path = os.path.join(get_root_path(), 'logs', 'usage.txt')
    
    models = {
        "C57-游泳/C57-Swimming": os.path.join(get_models_path(), "ABmodels/C57-Swimming-Trial-1-2024-11-21/config.yaml")
    }

    # 添加自定义CSS样式
    st.markdown("""
    <style>
        /* 卡片容器 */
        .stCard {
            background-color: white;
            padding: 2rem;
            border-radius: 0.8rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        /* 信息提示框 */
        .info-box {
            background-color: #e3f2fd;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 5px solid #2196F3;
            margin-bottom: 1.5rem;
        }
        
        /* 文件列表 */
        .file-list {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        /* 状态标签 */
        .status-label {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 1rem;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 0.2rem;
        }
        
        .status-success {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        
        .status-warning {
            background-color: #fff3e0;
            color: #ef6c00;
        }
        
        /* 分隔线 */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 1px solid #e0e0e0;
        }
        
        /* 标签页样式 */
        .stTabs {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* 模型选择框 */
        .model-select {
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        /* 日志显示区域 */
        .log-display {
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # 页面标题和说明
    st.title("🏊 小鼠游泳行为分析 / Mouse Swimming Analysis")
    
    with st.expander("💡 使用说明 / Instructions", expanded=True):
        st.markdown("""
        #### 视频要求 / Video Requirements:
        - 格式：MP4 / Format: MP4
        - 分辨率：550x550像素 / Resolution: 550x550 pixels
        - 帧率：30帧/秒 / Frame Rate: 30 fps
        
        #### 分析流程 / Analysis Process:
        1. 选择工作目录 / Choose working directory
        2. 上传视频文件 / Upload video files
        3. 选择分析模型 / Select analysis model
        4. 开始GPU分析 / Start GPU analysis
        5. 处理分析结果 / Process analysis results
        6. 下载结果文件 / Download result files
        
        #### GPU使用提示 / GPU Usage Note:
        - 如果GPU显存占用率很高，说明其他用户正在使用  
          If GPU memory usage is high, other users are currently using it
        - 请等待GPU资源释放后再开始新的工作  
          Please wait until GPU resources are available before starting new work
        """)

    tab1, tab2, tab3 = st.tabs([
        "📊 视频分析 / Video Analysis",
        "🔄 数据处理 / Result Process",
        "📥 结果下载 / Download"
    ])
    
    with tab1:
        # GPU状态显示
        st.subheader("🖥️ GPU 状态 / GPU Status")
        high_memory_usage = display_gpu_usage()

        # GPU配置
        st.subheader("⚙️ GPU 配置 / GPU Configuration")
        gpu_count, selected_gpus = setup_gpu_selection()
        if selected_gpus:
            st.success(f"可用GPU数量 / Available GPUs: {gpu_count}")
            st.info(f"已选择的GPU / Selected GPUs: {selected_gpus}")

        # 目录选择和文件上传
        st.subheader("📁 工作目录 / Working Directory")
        create_folder_if_not_exists(folder_path)
        directories = list_directories(root_directory)
        
        if directories:
            selected_directory = st.selectbox("📂 选择工作目录 / Choose a directory", directories)
            folder_path = os.path.join(root_directory, selected_directory)
            st.success(f"当前工作目录 / Current working folder: {folder_path}")
            
            # 文件上传区域
            with st.container():
                st.subheader("📤 文件上传 / File Upload")
                upload_files(folder_path)
                selected_files = select_video_files(folder_path)
                
                if selected_files:
                    st.markdown("### 📋 已选择的视频文件 / Selected video files")
                    for file in selected_files:
                        st.markdown(f"- {file}")
                else:
                    st.info("📭 未选择视频文件 / No video files selected")
            
            # 模型选择
            st.subheader("🤖 模型选择 / Model Selection")
            selected_model_name = st.selectbox(
                "选择分析模型 / Choose analysis model",
                list(models.keys()),
                help="选择适合您的实验对象的模型 / Select the model suitable for your experimental subject"
            )
            config_path = models[selected_model_name]
            st.success(f"已选择模型 / Selected model: {selected_model_name}")

            # 分析控制
            if high_memory_usage:
                st.warning("⚠️ GPU显存占用率高，请稍后再试 / High GPU memory usage detected. Please wait before starting analysis.")
            else:
                if st.button("🚀 开始GPU分析 / Start GPU Analysis", use_container_width=True):
                    try:
                        with open(web_log_file_path, "a", encoding='utf-8') as web_log_file:
                            web_log_file.write(f"\n{st.session_state['name']}, {current_time}\n")
                        create_and_start_analysis(folder_path, selected_files, config_path, gpu_count, current_time, selected_gpus)
                        st.success("✅ 分析已开始！请查看日志了解进度 / Analysis started! Check logs for progress.")
                    except Exception as e:
                        st.error(f"❌ 分析启动失败 / Failed to start analysis: {e}")

            # 日志显示
            st.subheader("📋 分析日志 / Analysis Logs")
            if st.button("🔄 刷新日志 / Refresh Logs"):
                last_log_entries = fetch_last_lines_of_logs(folder_path, gpu_count)
                for gpu, log_entry in last_log_entries.items():
                    with st.expander(f"GPU {gpu} 日志 / Log", expanded=True):
                        st.code(log_entry)
        else:
            st.error("⚠️ 未找到工作目录 / No directories found")

    with tab2:
        st.subheader("🔄 结果处理 / Result Processing")
        if 'selected_directory' in locals():
            st.info(f"当前工作目录 / Current working folder: {selected_directory}")
            st.info(f"当前使用的模型 / Current model: {selected_model_name}")
            
            if st.button("⚡ 处理分析结果 / Process Analysis Results", use_container_width=True):
                with st.spinner("处理中 / Processing..."):
                    process_swimming_files(folder_path)
                st.success("✅ 结果处理完成 / Analysis results processed")
        else:
            st.warning("⚠️ 请先在分析页面选择工作目录 / Please select a working directory in the analysis tab first")

    with tab3:
        st.subheader("📥 结果下载 / Result Download")
        if 'selected_directory' in locals():
            st.info(f"当前工作目录 / Current working folder: {selected_directory}")
            st.info(f"当前使用的模型 / Current model: {selected_model_name}")
            
            try:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📦 下载所有文件 / Download All Files", use_container_width=True):
                        filter_and_zip_files(folder_path)
                
                with col2:
                    if st.button("📄 下载除MP4外的所有文件 / Download All Except MP4", use_container_width=True):
                        filter_and_zip_files(folder_path, excluded_ext=['.mp4'])
                
                with col3:
                    if st.button("📊 仅下载CSV文件 / Download Only CSV", use_container_width=True):
                        filter_and_zip_files(folder_path, included_ext=['.csv'])
                
            except Exception as e:
                st.error(f"❌ 文件下载出错 / Error during file download: {e}")
        else:
            st.warning("⚠️ 请先在分析页面选择工作目录 / Please select a working directory in the analysis tab first")

if __name__ == "__main__":
    mouse_swimming_page()
