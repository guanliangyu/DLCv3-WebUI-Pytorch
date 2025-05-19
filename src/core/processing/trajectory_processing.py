#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

def filter_low_likelihood(df, likelihood_threshold=0.5):
    """
    根据置信度阈值过滤数据，将低于阈值的行的 (x, y) 坐标置为 NaN。
    """
    df_filtered = df.copy()
    mask = df_filtered["likelihood"] < likelihood_threshold
    df_filtered.loc[mask, ["x", "y"]] = np.nan
    return df_filtered

def filter_extreme_jumps(df, extreme_dist=200.0):
    """
    第一层过滤：快速剔除极端跳变点。
    如果当前帧与前一帧之间的距离超过 extreme_dist 像素，则视为极端离群点，将当前帧标记为 NaN。
    """
    df_filtered = df.copy()
    x = df_filtered["x"].values
    y = df_filtered["y"].values
    
    for i in range(1, len(df_filtered)):
        if np.isnan(x[i]) or np.isnan(x[i-1]):
            continue
        dist = np.sqrt((x[i] - x[i-1])**2 + (y[i] - y[i-1])**2)
        if dist > extreme_dist:
            x[i] = np.nan
            y[i] = np.nan

    df_filtered["x"] = x
    df_filtered["y"] = y
    return df_filtered

def filter_unreasonable_speed(df, max_speed_threshold=50.0, fps=60):
    """
    第二层过滤：根据最大速度阈值剔除异常点。
    如果与前一帧或后一帧间距过大（> max_speed_threshold），则将当前帧标记为 NaN。
    """
    df_filtered = df.copy()
    x = df_filtered["x"].values
    y = df_filtered["y"].values
    n = len(x)
    
    for i in range(n):
        if i == 0 or i == n - 1:
            continue
        
        if np.isnan(x[i]) or np.isnan(y[i]):
            continue
        
        # 当前帧与前一帧
        if not np.isnan(x[i-1]) and not np.isnan(y[i-1]):
            dist_prev = np.sqrt((x[i] - x[i-1])**2 + (y[i] - y[i-1])**2)
            if dist_prev > max_speed_threshold:
                x[i] = np.nan
                y[i] = np.nan
                continue
        
        # 当前帧与下一帧
        if i < n - 1:
            if not np.isnan(x[i+1]) and not np.isnan(y[i+1]):
                dist_next = np.sqrt((x[i+1] - x[i])**2 + (y[i+1] - y[i])**2)
                if dist_next > max_speed_threshold:
                    x[i] = np.nan
                    y[i] = np.nan
                    continue

    df_filtered["x"] = x
    df_filtered["y"] = y
    return df_filtered

def interpolate_missing_points(df):
    """
    对缺失的点（NaN）进行线性插值。
    """
    df_interpolated = df.copy()
    for coord in ["x", "y"]:
        valid_mask = ~df_interpolated[coord].isna()
        valid_indices = df_interpolated[valid_mask].index
        valid_values = df_interpolated.loc[valid_mask, coord].values
        
        if len(valid_indices) < 2:
            continue
        
        f = interp1d(valid_indices, valid_values, kind='linear', fill_value="extrapolate")
        df_interpolated[coord] = f(df_interpolated.index)
    return df_interpolated

def smooth_trajectory(df, window_length=7, polyorder=2):
    """
    使用 Savitzky-Golay 滤波对插值完成后的 (x,y) 做平滑。
    """
    df_smoothed = df.copy()
    for coord in ["x", "y"]:
        series = df_smoothed[coord].values
        if np.isnan(series).any():
            continue
        if len(series) >= window_length:
            df_smoothed[coord] = savgol_filter(series, window_length, polyorder)
    return df_smoothed

def filter_unreasonable_position(df, x_min=199, x_max=450, y_min=220, y_max=450):
    """
    过滤掉不在合理范围内的位置点。
    
    Args:
        df: 包含x, y坐标的DataFrame
        x_min: x坐标最小值 (199)
        x_max: x坐标最大值 (450)
        y_min: y坐标最小值 (220)
        y_max: y坐标最大值 (450)
    """
    df_filtered = df.copy()
    position_mask = (
        (df_filtered['x'] >= x_min) & 
        (df_filtered['x'] <= x_max) & 
        (df_filtered['y'] >= y_min) & 
        (df_filtered['y'] <= y_max)
    )
    
    # 将不合理位置的点标记为NaN
    df_filtered.loc[~position_mask, ['x', 'y']] = np.nan
    return df_filtered

def detect_grab_trajectories(df, 
                           fps=120.0,
                           barrier_region=(330, 450, 250, 400),  # (x_min, x_max, y_min, y_max)
                           start_region=(200, 300, 350, 450),
                           max_back_time=0.5,   # 向前回溯最多0.5秒
                           max_forward_time=0.2,  # 向后查找最多0.2秒
                           min_frame_gap=60     # 两次抓取之间的最小帧数间隔
                           ):
    """
    根据给定思路检测抓取轨迹:
      1. 当在挡板右侧区域 (barrier_region) 有检测到的点(候选帧 i_candidate)
      2. 向前最多0.5秒找起点: 满足 start_region 条件且 y 值最大的帧 i_start
      3. 向后最多0.2秒找终点: x 值最大的帧 i_end
      4. 返回 (i_start, i_candidate, i_end) 以及对应时间, 以此构成一次抓取
      5. 确保相邻抓取之间有足够的时间间隔

    参数:
    - df: 已过滤/插值后的 DataFrame, 包含列 'x','y'
    - fps: 视频帧率
    - barrier_region: 挡板右侧判定区域 (x_min, x_max, y_min, y_max)
    - start_region: 回溯时可能的起点区域 (x_min, x_max, y_min, y_max)
    - max_back_time: 向前回溯的最大时间(秒)
    - max_forward_time: 向后搜寻终点的最大时间(秒)
    - min_frame_gap: 两次抓取之间的最小帧数间隔

    返回:
    - events: List[ dict ], 每个包含:
        {
          'i_start':    int,
          'i_candidate': int,
          'i_end':      int,
          'start_time': float,
          'candidate_time': float,
          'end_time':   float
        }
    """
    # 区域解析
    bxmin, bxmax, bymin, bymax = barrier_region
    sxmin, sxmax, symin, symax = start_region

    # 将 df.x, df.y 取成 numpy 数组，便于快速索引
    x = df["x"].values
    y = df["y"].values
    n_frames = len(df)

    # 1) 找到所有落在挡板右侧区域的帧索引
    region_mask = (x > bxmin) & (x < bxmax) & (y > bymin) & (y < bymax)
    candidate_indices = np.where(region_mask)[0]

    startOffset = int(round(max_back_time * fps))      # 回溯最大帧数
    endOffset   = int(round(max_forward_time * fps))

    events = []
    used_frames = set()  # 记录已使用的帧

    # 按时间顺序处理候选点
    for i_candidate in sorted(candidate_indices):
        # 检查当前候选点是否在已使用的帧范围内
        if i_candidate in used_frames:
            continue

        # 检查是否与前一个事件有足够的时间间隔
        if events and i_candidate - events[-1]['i_end'] < min_frame_gap:
            continue

        # 2) 向前回溯不超过 max_back_time
        i_start_candidate_min = max(0, i_candidate - startOffset)
        # 找 [i_start_candidate_min, i_candidate] 区间内
        #  满足 start_region & y 值最大的帧
        best_i_start = None
        best_y = -np.inf
        for i_back in range(i_start_candidate_min, i_candidate+1):
            if i_back in used_frames:
                continue
            if (x[i_back] > sxmin and x[i_back] < sxmax and
                y[i_back] > symin and y[i_back] < symax):
                if y[i_back] > best_y:
                    best_y = y[i_back]
                    best_i_start = i_back

        if best_i_start is None:
            continue

        # 3) 向后找终点: 不超过 max_forward_time 的范围内 x 最大的帧
        i_end_candidate_max = min(n_frames-1, i_candidate + endOffset)
        best_i_end = None
        best_x = -np.inf
        for i_fwd in range(i_candidate, i_end_candidate_max+1):
            if i_fwd in used_frames:
                continue
            if x[i_fwd] > best_x:
                best_x = x[i_fwd]
                best_i_end = i_fwd

        if best_i_end is None:
            continue

        # 记录事件信息
        event_info = {
            'i_start': best_i_start,
            'i_candidate': i_candidate,
            'i_end': best_i_end,
            'start_time': best_i_start / fps,
            'candidate_time': i_candidate / fps,
            'end_time': best_i_end / fps
        }
        events.append(event_info)

        # 标记已使用的帧
        for frame in range(best_i_start, best_i_end + 1):
            used_frames.add(frame)

    return events

def plot_trajectory_with_events(df, events, fps=120.0, title="Trajectory with Barrier-based Grab"):
    """
    简单绘图展示 (x,y)，并标注每段轨迹的起点、候选点(挡板区域检测帧)、终点。
    """
    x = df["x"].values
    y = df["y"].values
    
    fig, ax = plt.subplots(figsize=(8,6))
    ax.plot(x, y, '-o', markersize=3, label='Mouse LeftHand')

    # 标注事件
    for idx, e in enumerate(events, 1):
        i_s, i_c, i_e = e['i_start'], e['i_candidate'], e['i_end']
        # 起点
        ax.plot(x[i_s], y[i_s], 'rs', label=f"Start {idx}" if idx==1 else "", markersize=6)
        ax.text(x[i_s], y[i_s], f"S{idx}\n{e['start_time']:.2f}s", color='red', fontsize=8)
        # 候选帧
        ax.plot(x[i_c], y[i_c], 'g^', label=f"Candidate {idx}" if idx==1 else "", markersize=6)
        ax.text(x[i_c], y[i_c], f"C{idx}\n{e['candidate_time']:.2f}s", color='green', fontsize=8)
        # 终点
        ax.plot(x[i_e], y[i_e], 'bv', label=f"End {idx}" if idx==1 else "", markersize=6)
        ax.text(x[i_e], y[i_e], f"E{idx}\n{e['end_time']:.2f}s", color='blue', fontsize=8)

    ax.invert_yaxis()  # 如果图像坐标向下为正，可反转 Y 轴
    ax.set_xlabel("X (pixels)")
    ax.set_ylabel("Y (pixels)")
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    return fig

def format_timestamp(seconds):
    """格式化时间戳为MM:SS.mmm格式"""
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:06.3f}" 