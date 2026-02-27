import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from typing import Any, Dict, List, Optional
from collections import Counter
import time
import traceback
from matplotlib.ticker import FuncFormatter


# ---------------------------------------
# 1. 行为分析主入口
# ---------------------------------------
def process_mouse_social_video(
    video_path: str,
    threshold: float = 0.999,
    min_duration_sec: float = 2.0,
    max_duration_sec: float = 35.0,
    fps: float = 30.0,
):
    """
    处理小鼠社交行为视频的分析结果, 并进行平滑、可视化和持续时间分析。

    Args:
        video_path (str): 原始视频文件路径, 用于匹配同名 _el.csv.
        threshold (float): 关键点置信度阈值(如0.999).
        min_duration_sec (float): 最小持续时间(秒), 默认2秒.
        max_duration_sec (float): 最大持续时间(秒), 默认35秒(可自行拆分).
        fps (float): 视频帧率, 默认30帧/秒.
    """
    try:
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]

        # 1. 寻找对应 _el.csv
        csv_files = [
            f
            for f in os.listdir(video_dir)
            if f.startswith(video_name) and f.endswith("_el.csv")
        ]
        if not csv_files:
            st.error(
                f"未找到对应的 CSV 文件 / No corresponding CSV file for: {video_name}"
            )
            return

        csv_path = os.path.join(video_dir, csv_files[0])
        df = pd.read_csv(csv_path, header=[0, 1, 2, 3])

        # 2. 分析行为并保存结果
        results_df, analysis_context = analyze_social_behavior(
            df,
            threshold=threshold,
            min_duration_sec=min_duration_sec,
            max_duration_sec=max_duration_sec,
            fps=fps,
        )

        # 3. 保存分析数据
        results_dir = save_analysis_data(
            video_name, video_dir, analysis_context, results_df
        )
        if results_dir is None:
            return

        # 4. 生成可视化图表
        figure_dir = os.path.join(results_dir, "figures")
        os.makedirs(figure_dir, exist_ok=True)

        plot_analysis_results(
            analysis_context, figure_dir=figure_dir, interaction_threshold=100.0
        )

        # 5. 在 Streamlit 中显示可视化
        st.success(f"分析完成! / Analysis done. 结果已保存至 {results_dir}")
        st.subheader("📊 分析结果 / Analysis Results")

        # 显示图表
        timeline_png = os.path.join(figure_dir, "behavior_timeline.png")
        distribution_png = os.path.join(figure_dir, "behavior_distribution.png")
        trajectory_png = os.path.join(figure_dir, "movement_trajectories.png")
        heatmap_png = os.path.join(figure_dir, "position_heatmaps.png")

        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists(timeline_png):
                st.image(timeline_png, caption="行为时间线 / Behavior Timeline")
            if os.path.exists(trajectory_png):
                st.image(trajectory_png, caption="运动轨迹 / Movement Trajectories")
        with col2:
            if os.path.exists(distribution_png):
                st.image(distribution_png, caption="行为分布 / Behavior Distribution")
            if os.path.exists(heatmap_png):
                st.image(heatmap_png, caption="位置热力图 / Position Heatmaps")

        # 显示结果表格
        if not results_df.empty:
            st.subheader("🎯 检测到的行为片段 / Detected Behavior Bouts")
            st.dataframe(results_df)

    except Exception as e:
        st.error(f"处理视频失败 / Failed to process video: {str(e)}")


# ---------------------------------------
# 2. 社交行为分析主函数
# ---------------------------------------
def analyze_social_behavior(
    df: pd.DataFrame,
    threshold: float,
    min_duration_sec: float,
    max_duration_sec: float,
    fps: float,
):
    """
    分析社交行为(帧级判定 + 滑动窗口平滑 + 行为段合并).
    返回: (持续时间统计结果DataFrame, {distance数组, angle数组...})
    """
    # 需要的关键点
    scorer = "DLC_Buctd-hrnetW48_SocialMar9shuffle1_detector_220_snapshot_110"  # 使用完整的scorer名称

    # 过滤有效的个体和关键点
    valid_individuals = ["individual1", "individual2"]  # 只保留两只老鼠
    valid_bodyparts = ["Mouth", "left-ear", "right-ear"]  # 只保留有效的关键点

    st.write("使用的个体:", valid_individuals)
    st.write("使用的关键点:", valid_bodyparts)

    coords = {}
    for individual in valid_individuals:
        for bp in valid_bodyparts:
            key = f"{individual}_{bp}"
            try:
                # 直接使用列名访问
                x = df[(scorer, individual, bp, "x")].values
                y = df[(scorer, individual, bp, "y")].values
                likelihood = df[(scorer, individual, bp, "likelihood")].values

                coords[key] = {"x": x, "y": y, "likelihood": likelihood}
            except KeyError as e:
                st.error(f"无法找到关键点数据: {key}, 错误: {str(e)}")
                st.write("可用的列:", df.columns.tolist())
                raise

    # 1) 帧级检测
    raw_frames = detect_social_frames(coords, threshold)

    # 2) 滑动窗口平滑(减少单帧抖动), 默认为0.5秒窗口
    half_second_frames = int(0.5 * fps)
    smoothed_types = smooth_behavior_sequence(
        raw_frames["social_types"], window_size=half_second_frames
    )
    raw_frames["social_types"] = smoothed_types

    # 3) 计算速度(示例: 嘴部在相邻帧间的移动速度)
    speeds_mouse1 = compute_speed(
        coords["individual1_Mouth"]["x"], coords["individual1_Mouth"]["y"], fps
    )
    speeds_mouse2 = compute_speed(
        coords["individual2_Mouth"]["x"], coords["individual2_Mouth"]["y"], fps
    )

    # 4) 行为段合并(≥ 2 秒)
    results = analyze_bout_duration(
        raw_frames,
        min_duration_sec=min_duration_sec,
        max_duration_sec=max_duration_sec,
        fps=fps,
    )
    results_df = pd.DataFrame(results)

    # 5) 收集位置数据用于轨迹和热力图
    positions = {
        "mouse1_x": coords["individual1_Mouth"]["x"],
        "mouse1_y": coords["individual1_Mouth"]["y"],
        "mouse2_x": coords["individual2_Mouth"]["x"],
        "mouse2_y": coords["individual2_Mouth"]["y"],
    }

    # 将一些可视化所需信息打包返回
    analysis_context = {
        "distance": raw_frames["mouse_distance"],
        "mouse1_angle": raw_frames["facing_angles"]["mouse1_angle"],
        "mouse2_angle": raw_frames["facing_angles"]["mouse2_angle"],
        "speeds_mouse1": speeds_mouse1,
        "speeds_mouse2": speeds_mouse2,
        "behavior_data": raw_frames["social_types"],  # 添加行为数据
        "positions": positions,  # 添加位置数据
    }

    return results_df, analysis_context


# ---------------------------------------
# 3. 帧级检测 & 平滑
# ---------------------------------------
def detect_social_frames(coords: dict, threshold: float) -> dict:
    """
    检测每一帧的社交行为
    """
    # 获取帧数
    frame_count = len(next(iter(coords.values()))["x"])
    st.write(f"总帧数: {frame_count}")

    # 有效帧(置信度过滤)
    valid_frames = np.ones(frame_count, dtype=bool)
    for key in coords:
        valid_frames &= coords[key]["likelihood"] > threshold

    st.write(f"有效帧数: {np.sum(valid_frames)}")

    # 计算距离和角度
    mouse_distance = calculate_mouse_distance(coords)
    facing_angles = calculate_facing_angles(coords)

    # 确保所有数组形状一致
    assert (
        len(mouse_distance) == frame_count
    ), f"Distance array shape mismatch: {len(mouse_distance)} vs {frame_count}"
    assert (
        len(facing_angles["mouse1_angle"]) == frame_count
    ), f"Angle array shape mismatch: {len(facing_angles['mouse1_angle'])} vs {frame_count}"

    # 行为类型判定
    social_types = determine_social_type(mouse_distance, facing_angles)

    return {
        "valid_frames": valid_frames,
        "mouse_distance": mouse_distance,
        "facing_angles": facing_angles,
        "social_types": social_types,
    }


def smooth_behavior_sequence(
    behavior_arr: np.ndarray, window_size: int = 15
) -> np.ndarray:
    """
    在给定的帧序列上, 用滑动窗口内多数表决的方式做平滑.
    window_size=15相当于前后7帧共15帧做投票.
    """
    n_frames = len(behavior_arr)
    smoothed = behavior_arr.copy()
    half_w = window_size // 2

    from collections import Counter

    for i in range(n_frames):
        start_idx = max(0, i - half_w)
        end_idx = min(n_frames, i + half_w + 1)
        window_slice = behavior_arr[start_idx:end_idx]

        counter = Counter(window_slice)
        top_label, _ = counter.most_common(1)[0]
        smoothed[i] = top_label

    return smoothed


# ---------------------------------------
# 4. 行为识别辅助
# ---------------------------------------
def determine_social_type(
    mouse_distance: np.ndarray, facing_angles: dict
) -> np.ndarray:
    """
    判断: 'interaction', 'proximity', or 'none'.
    """
    n_frames = len(mouse_distance)
    social_types = np.full(n_frames, "none", dtype=object)

    close_threshold = 100.0  # 距离阈值(像素)
    facing_threshold = 45.0  # 角度阈值(度)

    close_mask = mouse_distance < close_threshold

    # 双向朝向
    mutual_facing = (facing_angles["mouse1_angle"] < facing_threshold) & (
        facing_angles["mouse2_angle"] < facing_threshold
    )

    social_types[close_mask & mutual_facing] = "interaction"
    social_types[close_mask & ~mutual_facing] = "proximity"
    return social_types


def calculate_mouse_distance(coords: dict) -> np.ndarray:
    """
    计算两只小鼠之间的距离
    """
    try:
        # 计算每只老鼠的头部中心位置（使用嘴部位置）
        mouse1_cx = coords["individual1_Mouth"]["x"]
        mouse1_cy = coords["individual1_Mouth"]["y"]
        mouse2_cx = coords["individual2_Mouth"]["x"]
        mouse2_cy = coords["individual2_Mouth"]["y"]

        # 检查数据有效性
        if np.any(np.isnan([mouse1_cx, mouse1_cy, mouse2_cx, mouse2_cy])):
            st.warning("检测到坐标中存在无效值，将进行插值处理")
            # 对无效值进行线性插值
            for arr in [mouse1_cx, mouse1_cy, mouse2_cx, mouse2_cy]:
                if np.any(np.isnan(arr)):
                    valid_mask = ~np.isnan(arr)
                    if np.any(valid_mask):  # 确保有有效值可以用于插值
                        indices = np.arange(len(arr))
                        arr[~valid_mask] = np.interp(
                            indices[~valid_mask], indices[valid_mask], arr[valid_mask]
                        )

        # 计算欧氏距离
        dist: np.ndarray[Any, Any] = np.asarray(
            np.sqrt(
                np.square(mouse1_cx - mouse2_cx) + np.square(mouse1_cy - mouse2_cy)
            ),
            dtype=float,
        )

        # 验证计算结果
        if np.any(np.isnan(dist)):
            st.error("距离计算结果仍包含无效值，请检查原始数据")
            # 将剩余的NaN替换为一个合理的默认值
            dist = np.nan_to_num(dist, nan=1000.0)  # 使用1000像素作为默认距离

        st.write(f"距离数组形状: {dist.shape}")
        st.write(f"距离范围: [{np.nanmin(dist):.2f}, {np.nanmax(dist):.2f}]")

        return dist
    except Exception as e:
        st.error(f"计算距离时出错: {str(e)}")
        st.error(f"错误详情: {traceback.format_exc()}")
        # 返回一个默认的距离数组
        default_dist: np.ndarray[Any, Any] = np.full(
            len(next(iter(coords.values()))["x"]),
            1000.0,
            dtype=float,
        )
        return default_dist


def calculate_facing_angles(coords: dict) -> dict:
    """
    计算朝向角度
    """
    try:
        # 计算向量（从耳朵中点到嘴部）
        # 老鼠1
        mouse1_ear_cx = (
            coords["individual1_right-ear"]["x"] + coords["individual1_left-ear"]["x"]
        ) / 2.0
        mouse1_ear_cy = (
            coords["individual1_right-ear"]["y"] + coords["individual1_left-ear"]["y"]
        ) / 2.0
        mouse1_vec_x = coords["individual1_Mouth"]["x"] - mouse1_ear_cx
        mouse1_vec_y = coords["individual1_Mouth"]["y"] - mouse1_ear_cy

        # 老鼠2
        mouse2_ear_cx = (
            coords["individual2_right-ear"]["x"] + coords["individual2_left-ear"]["x"]
        ) / 2.0
        mouse2_ear_cy = (
            coords["individual2_right-ear"]["y"] + coords["individual2_left-ear"]["y"]
        ) / 2.0
        mouse2_vec_x = coords["individual2_Mouth"]["x"] - mouse2_ear_cx
        mouse2_vec_y = coords["individual2_Mouth"]["y"] - mouse2_ear_cy

        # 计算连接向量（从老鼠1到老鼠2）
        conn_x = mouse2_ear_cx - mouse1_ear_cx
        conn_y = mouse2_ear_cy - mouse1_ear_cy

        # 计算角度
        mouse1_angle = calculate_angle((mouse1_vec_x, mouse1_vec_y), (conn_x, conn_y))
        mouse2_angle = calculate_angle((mouse2_vec_x, mouse2_vec_y), (-conn_x, -conn_y))

        # 验证计算结果
        st.write(f"角度1数组形状: {mouse1_angle.shape}")
        st.write(f"角度1范围: [{mouse1_angle.min():.2f}, {mouse1_angle.max():.2f}]")
        st.write(f"角度2数组形状: {mouse2_angle.shape}")
        st.write(f"角度2范围: [{mouse2_angle.min():.2f}, {mouse2_angle.max():.2f}]")

        return {"mouse1_angle": mouse1_angle, "mouse2_angle": mouse2_angle}
    except Exception as e:
        st.error(f"计算角度时出错: {str(e)}")
        raise


def calculate_angle(vector1, vector2) -> np.ndarray:
    """
    计算两个向量之间的角度
    """
    v1x, v1y = vector1
    v2x, v2y = vector2

    # 计算点积
    dot = v1x * v2x + v1y * v2y

    # 计算向量模长
    mag1 = np.sqrt(v1x**2 + v1y**2)
    mag2 = np.sqrt(v2x**2 + v2y**2)

    # 计算夹角余弦值
    cos_angle = dot / (mag1 * mag2 + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    # 转换为角度
    angles: np.ndarray[Any, Any] = np.asarray(
        np.degrees(np.arccos(cos_angle)), dtype=float
    )
    return angles


# ---------------------------------------
# 5. 行为段合并
# ---------------------------------------
def analyze_bout_duration(
    social_frames: dict, min_duration_sec: float, max_duration_sec: float, fps: float
) -> list:
    """
    (和你之前的逻辑类似) 用 2秒合并逻辑, 并仅输出≥2秒的段.
    """
    valid_frames = social_frames["valid_frames"]
    social_types = social_frames["social_types"]

    mouse_distance = social_frames["mouse_distance"]
    mouse1_angle = social_frames["facing_angles"]["mouse1_angle"]
    mouse2_angle = social_frames["facing_angles"]["mouse2_angle"]

    frame_count = len(valid_frames)
    results = []

    min_duration_frames = int(min_duration_sec * fps)  # 转换为帧数
    gap_threshold_frames = int(2 * fps)  # 2秒的间隔阈值
    current_start = None
    current_behavior = None

    i = 0
    while i < frame_count:
        if valid_frames[i]:
            btype = social_types[i]
            if btype != "none":
                if current_start is None:
                    current_start = i
                    current_behavior = btype
                else:
                    # 如果发现新的行为和当前不一致, 检查gap
                    if btype != current_behavior:
                        if not can_merge_behavior(
                            social_frames, i, current_behavior, gap_threshold_frames
                        ):
                            # 结束前一段
                            results.extend(
                                close_bout_if_valid(
                                    current_start,
                                    i,
                                    current_behavior,
                                    mouse_distance,
                                    mouse1_angle,
                                    mouse2_angle,
                                    min_duration_frames,
                                    fps,
                                )
                            )
                            current_start = i
                            current_behavior = btype
            else:
                # 当前帧 'none'
                if current_start is not None:
                    if not can_merge_behavior(
                        social_frames, i, current_behavior, gap_threshold_frames
                    ):
                        results.extend(
                            close_bout_if_valid(
                                current_start,
                                i,
                                current_behavior,
                                mouse_distance,
                                mouse1_angle,
                                mouse2_angle,
                                min_duration_frames,
                                fps,
                            )
                        )
                        current_start = None
                        current_behavior = None
        else:
            # invalid frame
            if current_start is not None:
                if not can_merge_behavior(
                    social_frames, i, current_behavior, gap_threshold_frames
                ):
                    results.extend(
                        close_bout_if_valid(
                            current_start,
                            i,
                            current_behavior,
                            mouse_distance,
                            mouse1_angle,
                            mouse2_angle,
                            min_duration_frames,
                            fps,
                        )
                    )
                    current_start = None
                    current_behavior = None
        i += 1

    # 最后一段
    if current_start is not None:
        results.extend(
            close_bout_if_valid(
                current_start,
                frame_count,
                current_behavior,
                mouse_distance,
                mouse1_angle,
                mouse2_angle,
                min_duration_frames,
                fps,
            )
        )

    return results


def can_merge_behavior(
    social_frames: dict, start_idx: int, prev_behavior: Optional[str], gap_frames: int
) -> bool:
    if prev_behavior is None:
        return False

    valid_frames = social_frames["valid_frames"]
    social_types = social_frames["social_types"]
    n = len(valid_frames)

    end_search = min(start_idx + gap_frames, n)
    for j in range(start_idx, end_search):
        if valid_frames[j] and social_types[j] == prev_behavior:
            return True
    return False


def close_bout_if_valid(
    bout_start: int,
    bout_end: int,
    behavior: Optional[str],
    mouse_distance: np.ndarray,
    mouse1_angle: np.ndarray,
    mouse2_angle: np.ndarray,
    min_duration_frames: int,
    fps: float,
) -> List[Dict[str, Any]]:
    """
    检查并关闭一个行为片段，如果其持续时间大于等于最小持续时间则返回结果

    Args:
        bout_start: 片段开始帧
        bout_end: 片段结束帧
        behavior: 行为类型
        mouse_distance: 鼠间距离数组
        mouse1_angle: 鼠1角度数组
        mouse2_angle: 鼠2角度数组
        min_duration_frames: 最小持续帧数
        fps: 帧率
    """
    if behavior is None:
        return []

    duration = bout_end - bout_start
    if duration >= min_duration_frames:
        last_idx = bout_end - 1
        return [
            {
                "behavior_type": behavior,
                "start_frame": bout_start,
                "end_frame": last_idx,
                "start_s": bout_start / fps,
                "end_s": last_idx / fps,
                "duration_frames": duration,
                "duration_seconds": duration / fps,
                "distance": float(mouse_distance[last_idx]),
                "mouse1_angle": float(mouse1_angle[last_idx]),
                "mouse2_angle": float(mouse2_angle[last_idx]),
            }
        ]
    return []


# ---------------------------------------
# 6. 速度计算(示例)
# ---------------------------------------
def compute_speed(x_arr: np.ndarray, y_arr: np.ndarray, fps: float) -> np.ndarray:
    """
    简单相邻帧欧几里得距离 / (1/fps), 得到 px/s 速度
    """
    dx = np.diff(x_arr)
    dy = np.diff(y_arr)
    dist = np.sqrt(dx**2 + dy**2)
    speed = dist * fps  # px/frame -> px/s
    # 和 frame数对齐, 在前面插一个0
    speed = np.insert(speed, 0, 0.0)
    return speed


# ---------------------------------------
# 7. 结果可视化
# ---------------------------------------
def plot_analysis_results(
    analysis_context: dict, figure_dir: str, interaction_threshold: float = 100.0
):
    """
    生成并保存可视化图表
    """
    # 提取数据
    distance = analysis_context["distance"]
    mouse1_angle = analysis_context["mouse1_angle"]
    mouse2_angle = analysis_context["mouse2_angle"]
    speeds1 = analysis_context["speeds_mouse1"]
    speeds2 = analysis_context["speeds_mouse2"]
    behavior_data = analysis_context["behavior_data"]
    positions = analysis_context["positions"]

    # 定义时间格式化函数
    def format_time(x, p):
        """将帧数转换为 hh:mm:ss 格式，以整数化的分钟显示"""
        total_seconds = int(x / 30.0)  # 假设30fps
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}:00"

    # ---------- 1. 行为时间线图 ----------
    fig, ax = plt.subplots(figsize=(14, 4))  # 增加宽度以容纳右侧图例
    behaviors = ["interaction", "proximity", "none"]
    colors = {"interaction": "green", "proximity": "orange", "none": "gray"}

    for i, behavior in enumerate(behaviors):
        behavior_frames = [
            frame for frame, b in enumerate(behavior_data) if b == behavior
        ]
        if behavior_frames:
            ax.scatter(
                behavior_frames,
                [i] * len(behavior_frames),
                c=colors[behavior],
                label=behavior,
                s=1,
                alpha=0.6,
            )

    ax.set_yticks(range(len(behaviors)))
    ax.set_yticklabels(behaviors)

    # 设置x轴刻度 - 自适应间隔
    total_frames = len(behavior_data)
    total_minutes = (total_frames // 30) // 60  # 总分钟数

    # 根据总时长自适应调整间隔
    if total_minutes <= 10:  # 小于10分钟，每1分钟一个刻度
        interval_minutes = 1
    elif total_minutes <= 30:  # 小于30分钟，每2分钟一个刻度
        interval_minutes = 2
    elif total_minutes <= 60:  # 小于1小时，每5分钟一个刻度
        interval_minutes = 5
    elif total_minutes <= 120:  # 小于2小时，每10分钟一个刻度
        interval_minutes = 10
    else:  # 大于2小时，每30分钟一个刻度
        interval_minutes = 30

    # 计算刻度位置（以帧为单位）
    xticks = np.arange(0, total_frames + 1, 30 * 60 * interval_minutes)
    ax.set_xticks(xticks)
    ax.xaxis.set_major_formatter(FuncFormatter(format_time))
    plt.xticks(rotation=45)

    ax.set_xlabel("Time (hh:mm:ss)")
    ax.set_title("Behavior Timeline")
    # 将图例放在图的右侧
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()  # 自动调整布局以显示完整图例
    fig.savefig(
        os.path.join(figure_dir, "behavior_timeline.png"), dpi=150, bbox_inches="tight"
    )
    plt.close(fig)

    # ---------- 2. 行为比例柱状图 ----------
    fig, ax = plt.subplots(figsize=(8, 6))
    behavior_counts = Counter(behavior_data)
    total_frames = len(behavior_data)
    percentages = {
        b: (count / total_frames) * 100 for b, count in behavior_counts.items()
    }

    bars = ax.bar(percentages.keys(), percentages.values())
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Behavior Distribution")

    # 在柱子上添加具体数值
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    fig.savefig(os.path.join(figure_dir, "behavior_distribution.png"), dpi=150)
    plt.close(fig)

    # ---------- 3. 运动轨迹图 ----------
    if "positions" in analysis_context:
        fig, ax = plt.subplots(figsize=(10, 8))  # 增加宽度以容纳右侧图例

        # 绘制两只老鼠的轨迹
        ax.plot(
            positions["mouse1_x"],
            positions["mouse1_y"],
            "b-",
            alpha=0.5,
            label="Mouse 1",
            linewidth=1,
        )
        ax.plot(
            positions["mouse2_x"],
            positions["mouse2_y"],
            "r-",
            alpha=0.5,
            label="Mouse 2",
            linewidth=1,
        )

        # 标记起点和终点
        ax.plot(
            positions["mouse1_x"][0], positions["mouse1_y"][0], "bo", label="Start 1"
        )
        ax.plot(
            positions["mouse2_x"][0], positions["mouse2_y"][0], "ro", label="Start 2"
        )
        ax.plot(
            positions["mouse1_x"][-1], positions["mouse1_y"][-1], "bx", label="End 1"
        )
        ax.plot(
            positions["mouse2_x"][-1], positions["mouse2_y"][-1], "rx", label="End 2"
        )

        # 设置坐标轴
        ax.set_xlabel("X Position (pixels)")
        ax.set_ylabel("Y Position (pixels)")
        # 反转Y轴使其向下增加
        ax.invert_yaxis()
        ax.set_title("Movement Trajectories")
        # 将图例放在图的右侧
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()  # 自动调整布局以显示完整图例
        fig.savefig(
            os.path.join(figure_dir, "movement_trajectories.png"),
            dpi=150,
            bbox_inches="tight",
        )
        plt.close(fig)

        # ---------- 4. 位置热力图 ----------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 创建热力图数据 - 增加分辨率
        heatmap_resolution = 100  # 增加分辨率
        sigma = 2  # 高斯模糊参数

        def create_smooth_heatmap(x, y, x_edges, y_edges):
            # 创建初始热力图
            hist, _, _ = np.histogram2d(x, y, bins=[x_edges, y_edges])

            # 应用高斯模糊
            from scipy.ndimage import gaussian_filter

            hist_smooth = gaussian_filter(hist, sigma=sigma)

            # 对数变换增强低值区域
            hist_log = np.log1p(hist_smooth)  # log1p = log(1+x)
            # 重新归一化到[0,1]
            hist_normalized = hist_log / hist_log.max()
            return hist_normalized

        # 设置边界，添加边距
        margin = 50  # 像素边距
        x_min = min(positions["mouse1_x"].min(), positions["mouse2_x"].min()) - margin
        x_max = max(positions["mouse1_x"].max(), positions["mouse2_x"].max()) + margin
        y_min = min(positions["mouse1_y"].min(), positions["mouse2_y"].min()) - margin
        y_max = max(positions["mouse1_y"].max(), positions["mouse2_y"].max()) + margin

        x_edges = np.linspace(x_min, x_max, heatmap_resolution)
        y_edges = np.linspace(y_min, y_max, heatmap_resolution)

        # 创建自定义颜色映射
        from matplotlib.colors import LinearSegmentedColormap

        heatmap_colors = [
            (1, 1, 1, 0),  # 完全透明的白色作为背景
            (0.6, 0.6, 1, 0.3),  # 淡紫色，用于低热力区
            (0, 0.6, 1, 0.4),  # 天蓝色
            (0, 1, 0.6, 0.5),  # 青绿色
            (1, 1, 0, 0.7),  # 黄色
            (1, 0.6, 0, 0.8),  # 橙色
            (1, 0, 0, 1),  # 红色
        ]
        n_bins = 256  # 颜色分级数
        cmap = LinearSegmentedColormap.from_list("custom", heatmap_colors, N=n_bins)

        # Mouse 1热力图
        hist1_smooth = create_smooth_heatmap(
            positions["mouse1_x"], positions["mouse1_y"], x_edges, y_edges
        )
        im1 = ax1.imshow(
            hist1_smooth.T,
            origin="upper",
            extent=[x_min, x_max, y_max, y_min],
            cmap=cmap,
            interpolation="gaussian",
        )
        ax1.set_title("Mouse 1 Position Heatmap")
        plt.colorbar(im1, ax=ax1)

        # Mouse 2热力图
        hist2_smooth = create_smooth_heatmap(
            positions["mouse2_x"], positions["mouse2_y"], x_edges, y_edges
        )
        im2 = ax2.imshow(
            hist2_smooth.T,
            origin="upper",
            extent=[x_min, x_max, y_max, y_min],
            cmap=cmap,
            interpolation="gaussian",
        )
        ax2.set_title("Mouse 2 Position Heatmap")
        plt.colorbar(im2, ax=ax2)

        # 设置坐标轴格式
        for ax in [ax1, ax2]:
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.set_xlabel("X Position (pixels)")
            ax.set_ylabel("Y Position (pixels)")

        plt.tight_layout()
        fig.savefig(
            os.path.join(figure_dir, "position_heatmaps.png"),
            dpi=150,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )

    # ---------- 保存原有的图表 ----------
    # 距离随时间变化图
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(distance, label="Mouth-Mouth Distance", color="steelblue")
    ax.axhline(
        interaction_threshold, ls="--", color="red", label="Interaction threshold"
    )
    ax.set_xlabel("Frame")
    ax.set_ylabel("Distance (pixels)")
    ax.set_title("Mouth-Mouth Distance over Time")
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(figure_dir, "distance_over_time.png"), dpi=150)
    plt.close(fig)

    # 距离分布图
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(distance, bins=50, color="royalblue", alpha=0.7, edgecolor="black")
    ax.axvline(
        interaction_threshold, ls="--", color="red", label="Interaction threshold"
    )
    ax.set_xlabel("Distance (pixels)")
    ax.set_ylabel("Count")
    ax.set_title("Mouth-Mouth Distance Distribution")
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(figure_dir, "distance_distribution.png"), dpi=150)
    plt.close(fig)

    # 速度分布图
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(
        speeds1,
        bins=50,
        alpha=0.7,
        label="Ind1 Mouth Speed",
        color="blue",
        edgecolor="black",
    )
    ax.hist(
        speeds2,
        bins=50,
        alpha=0.7,
        label="Ind2 Mouth Speed",
        color="orange",
        edgecolor="black",
    )
    ax.set_xlabel("Speed (px/s)")
    ax.set_ylabel("Count")
    ax.set_title("Mouth Speed Distribution")
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(figure_dir, "speed_distribution.png"), dpi=150)
    plt.close(fig)

    # 头部角度随时间变化图
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(mouse1_angle, label="Mouse1 Head Angle", color="darkgreen")
    ax.plot(mouse2_angle, label="Mouse2 Head Angle", color="coral")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Angle (degrees)")
    ax.set_title("Head Angle Over Time")
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(figure_dir, "head_angle_over_time.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------
# 8. 保存结果
# ---------------------------------------
def save_results(results: pd.DataFrame, output_path: str):
    """
    保存分析结果到 CSV
    """
    try:
        results.to_csv(output_path, index=False)
        st.success(f"结果已保存 / Results saved: {output_path}")
    except Exception as e:
        st.error(f"保存结果失败 / Failed to save results: {str(e)}")


def save_analysis_data(
    video_name: str, video_dir: str, analysis_context: dict, results_df: pd.DataFrame
):
    """
    保存分析数据到文件

    Args:
        video_name (str): 视频文件名（不含扩展名）
        video_dir (str): 视频所在目录
        analysis_context (dict): 分析上下文数据
        results_df (pd.DataFrame): 行为分析结果
    """
    try:
        # 1. 尝试在原始目录创建结果文件夹
        results_dir = os.path.join(video_dir, f"{video_name}_results")
        try:
            os.makedirs(results_dir, exist_ok=True)
        except Exception as e:
            st.warning(f"无法在原始目录创建文件夹: {str(e)}")
            # 尝试在用户主目录下创建
            user_home = os.path.expanduser("~")
            results_dir = os.path.join(user_home, "DLCv3_Results", video_name)
            try:
                os.makedirs(results_dir, exist_ok=True)
                st.info(f"结果将保存至用户主目录: {results_dir}")
            except Exception as e:
                st.error(f"无法在用户主目录创建文件夹: {str(e)}")
                # 最后尝试使用临时目录
                import tempfile

                results_dir = os.path.join(
                    tempfile.gettempdir(), f"DLCv3_Results_{video_name}"
                )
                os.makedirs(results_dir, exist_ok=True)
                st.warning(f"使用临时目录: {results_dir}")

        # 2. 保存行为分析结果
        behavior_path = os.path.join(results_dir, "behavior_analysis.csv")
        try:
            # 如果文件已存在，直接覆盖
            results_df.to_csv(behavior_path, index=False, mode="w")
        except Exception as e:
            st.error(f"保存行为分析结果失败: {str(e)}")
            # 尝试使用时间戳创建新文件名
            behavior_path = os.path.join(
                results_dir, f"behavior_analysis_{int(time.time())}.csv"
            )
            results_df.to_csv(behavior_path, index=False)

        # 3. 保存详细数据
        detailed_data = pd.DataFrame(
            {
                "frame": np.arange(len(analysis_context["distance"])),
                "distance": analysis_context["distance"],
                "mouse1_angle": analysis_context["mouse1_angle"],
                "mouse2_angle": analysis_context["mouse2_angle"],
                "mouse1_speed": analysis_context["speeds_mouse1"],
                "mouse2_speed": analysis_context["speeds_mouse2"],
            }
        )

        data_path = os.path.join(results_dir, "detailed_data.csv")
        try:
            # 如果文件已存在，直接覆盖
            detailed_data.to_csv(data_path, index=False, mode="w")
        except Exception as e:
            st.error(f"保存详细数据失败: {str(e)}")
            # 尝试使用时间戳创建新文件名
            data_path = os.path.join(
                results_dir, f"detailed_data_{int(time.time())}.csv"
            )
            detailed_data.to_csv(data_path, index=False)

        st.success(f"分析数据已保存至: {results_dir}")
        return results_dir

    except Exception as e:
        st.error(f"保存分析数据失败: {str(e)}")
        st.error(f"错误详情: {traceback.format_exc()}")
        # 返回None但不中断程序
        return None
