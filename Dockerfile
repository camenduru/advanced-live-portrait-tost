FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04
WORKDIR /content
ENV PATH="/home/camenduru/.local/bin:${PATH}"
RUN adduser --disabled-password --gecos '' camenduru && \
    adduser camenduru sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R camenduru:camenduru /content && \
    chmod -R 777 /content && \
    chown -R camenduru:camenduru /home && \
    chmod -R 777 /home

RUN apt update -y && add-apt-repository -y ppa:git-core/ppa && apt update -y && apt install -y aria2 git git-lfs unzip ffmpeg

USER camenduru

RUN pip install -q opencv-python imageio imageio-ffmpeg ffmpeg-python av runpod \
    xformers==0.0.25 torchsde==0.2.6 einops==0.8.0 dill==0.3.8 ultralytics==8.2.102 diffusers==0.28.0 transformers==4.41.2 accelerate==0.30.1 && \
    git clone https://github.com/comfyanonymous/ComfyUI /content/ComfyUI && \
    git clone https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait /content/ComfyUI/custom_nodes/ComfyUI-AdvancedLivePortrait && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/appearance_feature_extractor.safetensors -d /content/ComfyUI/models/liveportrait -o appearance_feature_extractor.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/landmark.onnx -d /content/ComfyUI/models/liveportrait -o landmark.onnx && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/landmark_model.pth -d /content/ComfyUI/models/liveportrait -o landmark_model.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/motion_extractor.safetensors -d /content/ComfyUI/models/liveportrait -o motion_extractor.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/spade_generator.safetensors -d /content/ComfyUI/models/liveportrait -o spade_generator.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/stitching_retargeting_module.safetensors -d /content/ComfyUI/models/liveportrait -o stitching_retargeting_module.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/LivePortrait_InsightFace/resolve/main/liveportrait/human/warping_module.safetensors -d /content/ComfyUI/models/liveportrait -o warping_module.safetensors

COPY ./worker_runpod.py /content/ComfyUI/worker_runpod.py
WORKDIR /content/ComfyUI
CMD python worker_runpod.py