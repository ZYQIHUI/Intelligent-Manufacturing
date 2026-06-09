# -*- coding: utf-8 -*-
"""
手写数字识别 —— Streamlit 应用
================================
支持两种输入方式：上传图片 或 手写画布绘制，
加载训练好的 mnist_model.h5 进行实时预测。
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import cv2
from tensorflow import keras

# -------------------- 页面配置 --------------------
st.set_page_config(
    page_title="手写数字识别 Demo",
    page_icon="✍️",
    layout="centered"
)

st.title("✍️ 手写数字识别 Demo")
st.markdown("---")

# -------------------- 侧边栏：输入方式选择 --------------------
st.sidebar.header("输入设置")
input_mode = st.sidebar.radio(
    "选择输入方式：",
    ["A. 上传图片", "B. 手写画布"]
)

# -------------------- 加载模型（带缓存） --------------------
@st.cache_resource
def load_model():
    """加载训练好的 MNIST 模型"""
    model = keras.models.load_model("mnist_model.h5")
    return model

model = load_model()


# -------------------- 图像预处理函数 --------------------
def preprocess_image(img: Image.Image) -> tuple:
    """
    预处理图像以适配模型输入。

    步骤：
    1. 转灰度
    2. 缩放到 28x28
    3. 自动反色：使数字为白色 (255)，背景为黑色 (0)
    4. 归一化到 [0, 1]
    5. 调整维度为 (1, 28, 28, 1)

    返回：
        processed_img: 预处理后的图像 (PIL Image，用于显示)
        input_array: 模型输入数组 (1, 28, 28, 1)
    """
    # 1. 转灰度
    img = img.convert("L")

    # 2. 缩放到 28x28（使用 LANCZOS 高质量重采样）
    img = img.resize((28, 28), Image.LANCZOS)

    # 3. 自动反色
    #    将图像转为 numpy 数组
    img_array = np.array(img, dtype=np.float32)

    #    计算像素平均值：若平均值 > 127，说明背景偏白/数字偏黑，需要反色
    if np.mean(img_array) > 127:
        img_array = 255.0 - img_array
        img = Image.fromarray(img_array.astype(np.uint8))

    # 4. 归一化到 [0, 1]
    img_array = img_array / 255.0

    # 5. 调整维度 → (1, 28, 28, 1)
    input_array = img_array.reshape(1, 28, 28, 1)

    return img, input_array


def predict_digit(input_array: np.ndarray) -> tuple:
    """
    模型预测数字。

    返回：
        digit: 预测的数字 (0-9)
        confidence: 置信度 (百分比，保留两位小数)
    """
    predictions = model.predict(input_array, verbose=0)[0]  # 10 维概率向量
    digit = int(np.argmax(predictions))
    confidence = float(predictions[digit]) * 100.0
    return digit, confidence


# ==================== 输入方式 A：上传图片 ====================
if input_mode == "A. 上传图片":
    st.subheader("📤 上传手写数字图片")
    uploaded_file = st.file_uploader(
        "选择一张图片（支持 png / jpg / jpeg）",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        # 读取上传的图片
        raw_img = Image.open(uploaded_file)

        # 显示原始输入（限制显示宽度不超过 280）
        col1, col2 = st.columns(2)
        with col1:
            st.image(raw_img, caption="原始输入", width=280)

        # 预处理
        with st.spinner("正在处理图像 ..."):
            processed_img, input_array = preprocess_image(raw_img)

        # 显示预处理后的 28x28 图像（放大显示便于观察）
        with col2:
            st.image(processed_img, caption="预处理后 (28×28)", width=140)

        # 预测
        digit, confidence = predict_digit(input_array)

        # 展示结果
        st.markdown("---")
        st.success(f"### 🎯 预测结果：**{digit}**")
        st.metric(label="置信度", value=f"{confidence:.2f}%")

# ==================== 输入方式 B：手写画布 ====================
else:
    st.subheader("🖊️ 在下方画布中手写数字")

    # 动态导入 streamlit-drawable-canvas（避免缺少依赖时报错）
    try:
        from streamlit_drawable_canvas import st_canvas
    except ImportError:
        st.error(
            "缺少依赖 `streamlit-drawable-canvas`，请运行：\n"
            "```bash\npip install streamlit-drawable-canvas\n```"
        )
        st.stop()

    # 画布组件
    canvas_result = st_canvas(
        fill_color="black",            # 背景填充色（黑色）
        stroke_width=15,               # 笔画宽度
        stroke_color="white",          # 笔画颜色（白色）
        background_color="black",      # 背景色（黑色）
        width=280,                     # 画布宽度
        height=280,                    # 画布高度
        drawing_mode="freedraw",       # 自由手绘模式
        key="canvas"
    )

    # 当画布上有绘图数据时进行预测
    if canvas_result.image_data is not None:
        # canvas_result.image_data 是 numpy 数组，形状 (H, W, 4) RGBA
        img_array = canvas_result.image_data.astype(np.uint8)

        # 检查是否有笔画（非全黑）
        if img_array[:, :, :3].max() > 0:
            # 转为 PIL Image（RGBA → RGB → 灰度）
            img = Image.fromarray(img_array, "RGBA").convert("RGB")
            gray_img = ImageOps.grayscale(img)

            # 显示原始画布输入（自动转换为灰度显示）
            st.markdown("**原始输入：**")
            st.image(gray_img, caption="手写输入", width=280)

            # 预处理
            with st.spinner("正在处理图像 ..."):
                processed_img, input_array = preprocess_image(gray_img)

            # 显示预处理后的 28x28 图像
            col_img, col_result = st.columns([1, 2])
            with col_img:
                st.image(processed_img, caption="预处理后 (28×28)", width=140)

            # 预测
            digit, confidence = predict_digit(input_array)

            # 展示结果
            with col_result:
                st.markdown("---")
                st.success(f"### 🎯 预测结果：**{digit}**")
                st.metric(label="置信度", value=f"{confidence:.2f}%")
        else:
            st.info("👆 请在画布上绘制一个数字")
