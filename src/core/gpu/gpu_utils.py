import GPUtil
import streamlit as st

def get_gpu_utilization():
    gpus = GPUtil.getGPUs()
    gpu_usage = []
    for gpu in gpus:
        gpu_usage.append(f"GPU: {gpu.name}, Load: {gpu.load*100}%, Memory Usage: {gpu.memoryUsed}/{gpu.memoryTotal} MB")
    return gpu_usage

def display_gpu_usage():
    gpu_usage = get_gpu_utilization()
    high_memory_usage = False
    if gpu_usage:
        st.write("### GPU Utilization:")
        for usage in gpu_usage:
            st.write(usage)
            if "Memory Usage" in usage:
                memory_used = int(float(usage.split('Memory Usage:')[1].split('/')[0].strip()))
                if memory_used > 2000:  # Assuming 2000 MB as the threshold for high memory usage
                    high_memory_usage = True
    else:
        st.write("No GPU found or GPU utilization not available.")
    return high_memory_usage
