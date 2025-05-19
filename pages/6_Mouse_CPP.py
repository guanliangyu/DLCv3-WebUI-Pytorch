import streamlit as st
import os
import datetime
from src.core.config import get_root_path, get_data_path, get_models_path
from src.core.helpers.analysis_helper import create_and_start_analysis, fetch_last_lines_of_logs
from src.core.helpers.download_utils import filter_and_zip_files
from src.core.processing.mouse_cpp_video_processing import process_cpp_files

# 导入共享组件
from src.ui.components import render_sidebar, load_custom_css, show_gpu_status, setup_working_directory

# 设置页面配置
st.set_page_config(
    page_title="Mouse CPP",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置文件上传大小限制为40GB
st.markdown("""
    <style>
        [data-testid="stFileUploader"] {
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)
import streamlit.config as config
config.set_option('server.maxUploadSize', 40960)  # 设置为40GB (40 * 1024 MB)

# 加载样式和侧边栏
load_custom_css()
render_sidebar()

# 页面标题和说明
st.title("📍 位置偏好分析 / Mouse CPP Analysis")

with st.expander("💡 使用说明 / Instructions", expanded=False):
    st.markdown("""
    #### 视频要求 / Video Requirements:
    - 格式：MP4 / Format: MP4
    - 分辨率：500x500像素 / Resolution: 500x500 pixels
    - 帧率：30帧/秒 / Frame Rate: 30 fps
    """)

# 设置路径和时间
root_directory = os.path.join(get_data_path(), 'mouse_cpp')
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
web_log_file_path = os.path.join(get_root_path(), 'logs', 'usage.txt')

# 设置工作目录
folder_path, selected_files = setup_working_directory(root_directory)

# 设置模型
models = {
    "ICR-DJ-CPP-V2": os.path.join(get_models_path(), "DJ-cpp-500px-narrow-2024-05-13/config.yaml"),
    "C57-DJ-CPP-V2": os.path.join(get_models_path(), "C57-CPP-T2-2024-05-15/config.yaml")
}

# 检查可用的模型
available_models = {}
for name, path in models.items():
    if os.path.exists(path):
        available_models[name] = path

# 显示模型路径信息
st.write("### 模型路径信息 / Model Path Information:")
st.write(f"模型根目录 / Models root directory: {get_models_path()}")
for name, path in models.items():
    st.write(f"{name}: {path}")

tab1, tab2, tab3 = st.tabs([
    "📊 视频分析 / Video Analysis",
    "🔄 数据处理 / Result Process",
    "📥 结果下载 / Download"
])

with tab1:
    # 显示GPU状态
    high_memory_usage, gpu_count, selected_gpus = show_gpu_status()
    
    if folder_path and selected_files:
        # 模型选择
        st.subheader("🤖 模型选择 / Model Selection")
        
        if available_models:
            selected_model_name = st.selectbox(
                "选择分析模型 / Choose analysis model",
                list(available_models.keys()),
                help="选择适合您的实验对象的模型 / Select the model suitable for your experimental subject"
            )
            config_path = available_models[selected_model_name]
            st.success(f"已选择模型 / Selected model: {selected_model_name}")
        else:
            st.error("❌ 未找到可用的模型文件，请检查模型安装 / No available models found, please check model installation")
            st.stop()  # 停止页面执行
        
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

with tab2:
    st.subheader("🔄 结果处理 / Result Processing")
    if folder_path:
        st.info(f"当前工作目录 / Current working folder: {os.path.basename(folder_path)}")
        st.info(f"当前使用的模型 / Current model: {selected_model_name if 'selected_model_name' in locals() else 'Not selected'}")
        
        if st.button("⚡ 处理分析结果 / Process Analysis Results", use_container_width=True):
            with st.spinner("处理中 / Processing..."):
                process_cpp_files(folder_path, 0.999, 15, 35)
            st.success("✅ 结果处理完成 / Analysis results processed")
    else:
        st.warning("⚠️ 请先在分析页面选择工作目录 / Please select a working directory in the analysis tab first")

with tab3:
    st.subheader("📥 结果下载 / Result Download")
    if folder_path:
        st.info(f"当前工作目录 / Current working folder: {os.path.basename(folder_path)}")
        st.info(f"当前使用的模型 / Current model: {selected_model_name if 'selected_model_name' in locals() else 'Not selected'}")
        
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