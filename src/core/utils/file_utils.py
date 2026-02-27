import os
from typing import List, Optional

import streamlit as st


def _resolve_safe_upload_path(folder_path: str, filename: str) -> Optional[str]:
    """Return a safe path for uploaded files or None for invalid names."""
    normalized_name = filename.replace("\\", "/").strip()
    safe_name = os.path.basename(normalized_name)

    # Reject any upload name containing path traversal or directory segments.
    if not safe_name or safe_name in {".", ".."} or safe_name != normalized_name:
        return None

    base_dir = os.path.abspath(folder_path)
    candidate_path = os.path.abspath(os.path.join(base_dir, safe_name))

    try:
        if os.path.commonpath([base_dir, candidate_path]) != base_dir:
            return None
    except ValueError:
        return None

    return candidate_path


def create_new_folder(folder_path: str) -> bool:
    """创建新文件夹
    Create a new folder

    Args:
        folder_path (str): 文件夹路径

    Returns:
        bool: 是否创建成功
    """
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return True
        return False
    except Exception as e:
        st.error(f"创建文件夹失败 / Failed to create folder: {str(e)}")
        return False


def upload_files(folder_path: str) -> List[str]:
    """处理文件上传
    Handle file upload

    Args:
        folder_path (str): 上传目标目录
    """
    try:
        uploaded_files = st.file_uploader(
            "选择要上传的文件 / Choose files to upload",
            accept_multiple_files=True,
            type=["mp4"],
        )
        saved_files: List[str] = []

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = _resolve_safe_upload_path(folder_path, uploaded_file.name)
                if file_path is None:
                    st.error(
                        f"非法文件名，已拒绝上传 / Invalid file name rejected: {uploaded_file.name}"
                    )
                    continue

                with open(file_path, "wb") as file_handle:
                    file_handle.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
                st.success(
                    f"文件上传成功 / File uploaded successfully: {os.path.basename(file_path)}"
                )
        return saved_files
    except Exception as e:
        st.error(f"文件上传失败 / Failed to upload files: {str(e)}")
        return []


def list_directories(root_directory: str) -> List[str]:
    """列出目录下的所有子目录
    List all subdirectories in the directory

    Args:
        root_directory (str): 根目录路径

    Returns:
        List[str]: 子目录列表
    """
    try:
        if not os.path.exists(root_directory):
            return []
        return [
            d
            for d in os.listdir(root_directory)
            if os.path.isdir(os.path.join(root_directory, d))
        ]
    except Exception as e:
        st.error(f"列出目录失败 / Failed to list directories: {str(e)}")
        return []


def display_folder_contents(
    folder_path: str, selected_files: Optional[List[str]] = None
) -> None:
    """显示文件夹内容
    Display folder contents

    Args:
        folder_path (str): 文件夹路径
        selected_files (List[str], optional): 选中的文件列表
    """
    try:
        if not os.path.exists(folder_path):
            st.warning("⚠️ 文件夹不存在 / Folder does not exist")
            return

        files = os.listdir(folder_path)
        if not files:
            st.info("📭 文件夹为空 / Folder is empty")
            return

        st.write("### 📋 文件列表 / File List")
        for file in files:
            if selected_files and file in selected_files:
                st.success(f"✅ {file}")
            else:
                st.write(f"- {file}")
    except Exception as e:
        st.error(f"显示文件夹内容失败 / Failed to display folder contents: {str(e)}")


def create_folder_if_not_exists(folder_path: str) -> bool:
    """如果文件夹不存在则创建
    Create folder if it does not exist

    Args:
        folder_path (str): 文件夹路径

    Returns:
        bool: 是否创建成功或已存在
    """
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            st.success(f"创建文件夹成功 / Created folder: {folder_path}")
        return True
    except Exception as e:
        st.error(f"创建文件夹失败 / Failed to create folder: {str(e)}")
        return False


def select_video_files(folder_path: str) -> List[str]:
    """选择视频文件
    Select video files

    Args:
        folder_path (str): 文件夹路径

    Returns:
        List[str]: 选中的视频文件路径列表
    """
    try:
        if not os.path.exists(folder_path):
            return []

        # 获取目录下所有MP4文件
        video_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")]

        if not video_files:
            st.warning("⚠️ 未找到MP4视频文件 / No MP4 files found")
            return []

        # 让用户选择要处理的视频文件
        selected_files = st.multiselect(
            "选择需要处理的文件 / Select files to process",
            options=video_files,
            help="可以选择多个视频文件进行处理 / You can select multiple video files to process",
        )

        # 返回选中文件的完整路径
        return [os.path.join(folder_path, f) for f in selected_files]
    except Exception as e:
        st.error(f"选择视频文件失败 / Failed to select video files: {str(e)}")
        return []


def select_python_files(folder_path: str) -> List[str]:
    """选择Python文件
    Select Python files

    Args:
        folder_path (str): 文件夹路径

    Returns:
        List[str]: 选中的Python文件路径列表
    """
    try:
        if not os.path.exists(folder_path):
            return []

        python_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".py")]
        return [os.path.join(folder_path, f) for f in python_files]
    except Exception as e:
        st.error(f"选择Python文件失败 / Failed to select Python files: {str(e)}")
        return []
