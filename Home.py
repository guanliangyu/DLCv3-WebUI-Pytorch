import streamlit as st
import os
import datetime
from src.core.config import get_root_path, load_config, initialize_authenticator
from src.ui.components import render_sidebar, load_custom_css

# 设置页面配置
st.set_page_config(
    page_title="DLC-WebUI",
    page_icon="🐁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载自定义CSS样式
load_custom_css()

def initialize_app():
    """初始化应用程序"""
    st.markdown('<h1 class="main-title">🐁 DLC-WebUI</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 欢迎使用 DLC-WebUI / Welcome to DLC-WebUI
    
    这是一个基于DeepLabCut的小鼠行为分析系统。
    This is a mouse behavior analysis system based on DeepLabCut.
    
    #### 主要功能 / Main Features:
    1. 🎥 视频预处理 / Video Preprocessing
    2. ✂️ 视频裁剪 / Video Cropping
    3. 🔍 行为分析 / Behavior Analysis
       - 🐁 抓挠行为 / Scratch Behavior
       - 🐁 理毛行为 / Grooming Behavior
       - 🐁 游泳行为 / Swimming Behavior
       - 🏠 三箱实验 / Three Chamber Test
       - 👥 两鼠社交 / Two Social Test
       - 📍 位置偏好 / CPP Test
       - 🎯 抓取行为 / Catch Behavior
    4. 📊 数据分析 / Data Analysis
    5. 📥 结果导出 / Result Export
    """)

def main():
    """主函数"""
    # 加载配置和初始化认证器
    config = load_config(os.path.join(get_root_path(), 'src', 'core', 'config', 'config.yaml'))
    authenticator = initialize_authenticator(config)
    
    if authenticator:
        # 将登录组件放置于侧边栏顶部
        authenticator.login(location="sidebar", fields={"Form name": "登录系统 / Login System"})
        
        # 登录状态检查
        if st.session_state["authentication_status"] is False:
            st.error('用户名或密码错误 / Username/password is incorrect')
            st.stop()  # 停止渲染本次执行，等待用户修改输入
        elif st.session_state["authentication_status"] is None:
            st.warning('请输入用户名和密码 / Please enter your username and password')
            st.stop()  # 停止渲染本次执行，也会保持登录表单可继续交互
    
    # 调用功能导航组件，此时登录组件已位于侧边栏顶部
    initialize_app()

if __name__ == "__main__":
    main()
    render_sidebar()
