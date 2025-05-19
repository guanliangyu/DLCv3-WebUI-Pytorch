from .mouse_scratch_video_processing import (
    process_mouse_scratch_video,
    process_scratch_files
)

from .three_chamber_video_processing import (
    process_mouse_tc_video,
    process_tc_files,
    analyze_tc_behavior,
    detect_tc_frames
)

from .mouse_grooming_video_processing import (
    process_mouse_grooming_video,
    process_grooming_files,
    analyze_grooming_behavior,
    detect_grooming_frames
)

from .mouse_cpp_video_processing import (
    process_mouse_cpp_video,
    process_cpp_files,
    analyze_cpp_behavior,
    detect_position
)

from .mouse_swimming_video_processing import (
    process_mouse_swimming_video,
    process_swimming_files,
    analyze_swimming_behavior,
    detect_swimming_frames
)

from .mouse_social_video_processing import process_mouse_social_video, analyze_social_behavior, detect_social_frames

__all__ = [
    # 抓挠行为分析 / Scratch behavior analysis
    'process_mouse_scratch_video',
    'process_scratch_files',
    
    # 理毛行为分析 / Grooming behavior analysis
    'process_mouse_grooming_video',
    'process_grooming_files',
    'analyze_grooming_behavior',
    'detect_grooming_frames',
    
    # 三箱实验分析 / Three-chamber test analysis
    'process_mouse_tc_video',
    'process_tc_files',
    'analyze_tc_behavior',
    'detect_tc_frames',
    
    # CPP实验分析 / CPP test analysis
    'process_mouse_cpp_video',
    'process_cpp_files',
    'analyze_cpp_behavior',
    'detect_position',
    
    # 游泳行为分析 / Swimming behavior analysis
    'process_mouse_swimming_video',
    'process_swimming_files',
    'analyze_swimming_behavior',
    'detect_swimming_frames',
    
    # 社交行为分析 / Social behavior analysis
    'process_mouse_social_video',
    'analyze_social_behavior',
    'detect_social_frames'
] 