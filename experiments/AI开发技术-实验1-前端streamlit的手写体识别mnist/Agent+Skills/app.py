# -*- coding: utf-8 -*-
"""
手写数字识别 —— Streamlit 应用（PyTorch 版）
==============================================
加载训练好的 model.pth（MNISTCNN），支持两种输入方式：
A. 上传图片
B. 手写画布绘制
"""

import streamlit as st
import numpy as np
import torch
from PIL import Image, ImageOps

from mnist.model import MNISTCNN

# -------------------- 页面配置 --------------------
st.set_page_config(
    page_title="手写数字识别 Demo (PyTorch)",
    page_icon="✍️",
    layout="centered",
)

st.title("✍️ 手写数字识别 Demo")
st.caption("基于 PyTorch + MNIST CNN，测试准确率 99.31%")
st.markdown("---")

# -------------------- 加载模型 --------------------
@st.cache_resource
def load_model(device: str = "cpu"):
    model = MNISTCNN()
    state_dict = torch.load("model.pth", map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model, device


device = "cuda" if torch.cuda.is_available() else "cpu"
model, dev = load_model(device)

# -------------------- 图像预处理 --------------------
def preprocess_image(img: Image.Image) -> tuple[Image.Image, torch.Tensor]:
    """
    预处理步骤：
    1. 转灰度
    2. 缩放到 28×28
    3. 自动反色（确保数字为白色、背景为黑色）
    4. 归一化到 [0, 1]
    5. → (1, 1, 28, 28) 张量
    """
    # 1. 灰度
    img = img.convert("L")

    # 2. 缩放
    img = img.resize((28, 28), Image.LANCZOS)

    # 3. 自动反色
    img_array = np.array(img, dtype=np.float32)
    if np.mean(img_array) > 127:
        img_array = 255.0 - img_array
        img = Image.fromarray(img_array.astype(np.uint8))

    # 4. 归一化 [0, 1]
    img_array = img_array / 255.0

    # 5. → (1, 1, 28, 28)
    tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0)

    return img, tensor


def predict(tensor: torch.Tensor) -> tuple[int, float, np.ndarray]:
    """返回 (预测数字, 置信度百分比, 概率分布)"""
    with torch.no_grad():
        output = model(tensor.to(dev))
        probs = torch.softmax(output, dim=1)
        digit = int(torch.argmax(probs, dim=1).item())
        confidence = float(probs[0, digit].item()) * 100.0
    return digit, confidence, probs.cpu().numpy()[0]


# ==================== 侧边栏：输入方式选择 ====================
st.sidebar.header("输入设置")
input_mode = st.sidebar.radio(
    "选择输入方式：",
    ["A. 上传图片", "B. 手写画布"],
)

# ==================== 方式 A：上传图片 ====================
if input_mode == "A. 上传图片":
    st.subheader("📤 上传手写数字图片")
    uploaded_file = st.file_uploader(
        "选择一张图片（支持 png / jpg / jpeg）",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        raw_img = Image.open(uploaded_file)

        col1, col2 = st.columns(2)
        with col1:
            st.image(raw_img, caption="原始输入", width=280)

        with st.spinner("正在处理图像 ..."):
            processed_img, tensor = preprocess_image(raw_img)

        with col2:
            st.image(processed_img, caption="预处理后 (28×28)", width=140)

        digit, confidence, probs = predict(tensor)

        st.markdown("---")
        st.success(f"### 🎯 预测结果：**{digit}**")
        st.metric(label="置信度", value=f"{confidence:.2f}%")

        # 显示概率分布柱状图
        st.markdown("**概率分布：**")
        st.bar_chart({str(i): float(probs[i]) for i in range(10)})

# ==================== 方式 B：手写画布 ====================
else:
    st.subheader("🖊️ 在下方画布中手写数字")

    try:
        from streamlit_drawable_canvas import st_canvas
    except ImportError:
        st.error(
            "缺少依赖 `streamlit-drawable-canvas`，请运行：\n"
            "```bash\npip install streamlit-drawable-canvas\n```"
        )
        st.stop()

    canvas_result = st_canvas(
        fill_color="black",
        stroke_width=15,
        stroke_color="white",
        background_color="black",
        width=280,
        height=280,
        drawing_mode="freedraw",
        key="canvas",
    )

    if canvas_result.image_data is not None:
        img_array = canvas_result.image_data.astype(np.uint8)

        if img_array[:, :, :3].max() > 0:
            # RGBA → 灰度
            img = Image.fromarray(img_array, "RGBA").convert("RGB")
            gray_img = ImageOps.grayscale(img)

            st.markdown("**原始输入：**")
            st.image(gray_img, caption="手写输入", width=280)

            with st.spinner("正在处理图像 ..."):
                processed_img, tensor = preprocess_image(gray_img)

            col_img, col_result = st.columns([1, 2])
            with col_img:
                st.image(processed_img, caption="预处理后 (28×28)", width=140)

            digit, confidence, probs = predict(tensor)

            with col_result:
                st.markdown("---")
                st.success(f"### 🎯 预测结果：**{digit}**")
                st.metric(label="置信度", value=f"{confidence:.2f}%")
                st.markdown("**概率分布：**")
                st.bar_chart({str(i): float(probs[i]) for i in range(10)})
        else:
            st.info("👆 请在画布上绘制一个数字")
