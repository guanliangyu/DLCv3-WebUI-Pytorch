import GPUtil
import streamlit as st

def setup_gpu_selection():
    """
    Detects GPUs using GPUtil and sets up GPU selection in Streamlit.
    Returns the total count of GPUs and a list of selected GPU indices.
    """
    # Attempt to detect GPUs using GPUtil
    gpus = GPUtil.getGPUs()
    num_gpus = len(gpus)  # Get the number of GPUs available

    if num_gpus > 1:
        st.write(f"{num_gpus} GPUs detected in the system.")
        # Allow the user to specify how many GPUs they want to use
        gpu_count = st.number_input('Enter the number of GPUs available', min_value=1, value=2, max_value=num_gpus)
        # Allow the user to select specific GPUs (index-based)
        use_gpus = st.multiselect('Select GPUs to use', options=range(num_gpus), default=list(range(gpu_count)))
    elif num_gpus == 1:
        st.write("1 GPU detected in the system.")
        gpu_count = 1
        use_gpus = [0]  # Only one GPU available
    else:
        st.write("No GPUs detected in the system.")
        gpu_count = 0
        use_gpus = []

    return gpu_count, use_gpus
