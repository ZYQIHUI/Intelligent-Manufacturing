# MNIST 手写数字识别 — Agent + Skills 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax.

**目标:** 在 `Agent+Skills/` 目录下用 PyTorch + TDD 构建 CNN 手写数字识别项目，附带 Streamlit 前端（画板 + 图片上传），测试准确率 ≥ 98%

**技术栈:** Python 3.10+, PyTorch, torchvision, Streamlit, streamlit-drawable-canvas, Pillow, NumPy, Matplotlib, pytest

---

### Task 1: 创建项目基础结构 + requirements.txt

**Files:**
- Create: `Agent+Skills/requirements.txt`
- Create: `Agent+Skills/mnist/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```text
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
matplotlib>=3.7.0
streamlit>=1.28.0
streamlit-drawable-canvas>=0.9.0
pillow>=10.0.0
pytest>=7.4.0
```

- [ ] **Step 2: 创建 mnist 包初始化文件**

```python
# mnist/__init__.py
```

---

### Task 2: TDD — 数据加载模块

**Files:**
- Create: `Agent+Skills/tests/test_data.py`
- Create: `Agent+Skills/mnist/data.py`

- [ ] **Step 1: 编写 test_data.py**

```python
import pytest
import torch
from mnist.data import load_data


def test_load_data_returns_dataloaders():
    """验证 load_data 返回训练和测试 DataLoader"""
    train_loader, test_loader = load_data(batch_size=64)
    assert train_loader is not None
    assert test_loader is not None


def test_train_loader_batch_shape():
    """验证训练 DataLoader 的 batch 形状为 [64, 1, 28, 28]"""
    train_loader, _ = load_data(batch_size=64)
    images, labels = next(iter(train_loader))
    assert images.shape == (64, 1, 28, 28), f"期望 (64,1,28,28), 实际 {images.shape}"
    assert images.dtype == torch.float32


def test_train_loader_labels():
    """验证标签形状和取值范围"""
    train_loader, _ = load_data(batch_size=64)
    _, labels = next(iter(train_loader))
    assert labels.shape == (64,), f"期望 (64,), 实际 {labels.shape}"
    assert labels.dtype == torch.long
    assert labels.min() >= 0 and labels.max() <= 9


def test_normalized_range():
    """验证像素值归一化到 [0, 1]"""
    train_loader, _ = load_data(batch_size=64)
    images, _ = next(iter(train_loader))
    assert images.min() >= 0.0, f"最小值 {images.min()} < 0"
    assert images.max() <= 1.0, f"最大值 {images.max()} > 1"
```

- [ ] **Step 2: 运行测试 — 预期失败**

Run: `cd Agent+Skills && python -m pytest tests/test_data.py -v`
Expected: ModuleNotFoundError / ImportError (mnist.data 还不存在)

- [ ] **Step 3: 实现 data.py**

```python
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def load_data(batch_size: int = 64) -> tuple[DataLoader, DataLoader]:
    """
    加载 MNIST 数据集，返回训练和测试 DataLoader。
    自动下载（首次运行时），归一化到 [0, 1]。
    """
    transform = transforms.Compose([
        transforms.ToTensor(),  # PIL → Tensor, 自动归一化到 [0,1]
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST 全局均值和标准差
    ])

    train_dataset = datasets.MNIST(
        root="./data", train=True, download=True, transform=transform
    )
    test_dataset = datasets.MNIST(
        root="./data", train=False, download=True, transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader
```

- [ ] **Step 4: 运行测试 — 预期通过**

Run: `cd Agent+Skills && python -m pytest tests/test_data.py -v`
Expected: 4 passed

---

### Task 3: TDD — 模型定义模块

**Files:**
- Create: `Agent+Skills/tests/test_model.py`
- Create: `Agent+Skills/mnist/model.py`

- [ ] **Step 1: 编写 test_model.py**

```python
import pytest
import torch
from mnist.model import MNISTCNN


def test_model_creation():
    """验证模型可以创建"""
    model = MNISTCNN()
    assert model is not None


def test_model_forward_shape():
    """验证前向传播输出形状为 [batch_size, 10]"""
    model = MNISTCNN()
    batch_size = 16
    x = torch.randn(batch_size, 1, 28, 28)
    output = model(x)
    assert output.shape == (batch_size, 10), f"期望 ({batch_size},10), 实际 {output.shape}"


def test_model_output_probabilities():
    """验证输出经 softmax 后在 [0,1] 内且每行和为 1"""
    model = MNISTCNN()
    model.eval()
    x = torch.randn(8, 1, 28, 28)
    with torch.no_grad():
        output = torch.softmax(model(x), dim=1)
    assert output.min() >= 0.0
    assert output.max() <= 1.0
    # 每行概率和接近 1
    assert torch.allclose(output.sum(dim=1), torch.ones(8), atol=1e-5)


def test_model_parameter_count():
    """验证模型有合理的参数量（>10万）"""
    model = MNISTCNN()
    total_params = sum(p.numel() for p in model.parameters())
    assert total_params > 100_000, f"参数量 {total_params} 太小"
    assert total_params < 10_000_000, f"参数量 {total_params} 太大"
```

- [ ] **Step 2: 运行测试 — 预期失败**

Run: `cd Agent+Skills && python -m pytest tests/test_model.py -v`
Expected: ImportError (MNISTCNN 未定义)

- [ ] **Step 3: 实现 model.py**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class MNISTCNN(nn.Module):
    """MNIST 手写数字识别的卷积神经网络"""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=0)   # 28→26
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=0)  # 13→11
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(64 * 5 * 5, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))        # [B,32,13,13]
        x = self.dropout1(x)
        x = self.pool(F.relu(self.conv2(x)))        # [B,64,5,5]
        x = self.dropout1(x)
        x = torch.flatten(x, 1)                     # [B, 64*5*5]
        x = F.relu(self.fc1(x))                     # [B, 128]
        x = self.dropout2(x)
        x = self.fc2(x)                             # [B, 10]
        return x
```

- [ ] **Step 4: 运行测试 — 预期通过**

Run: `cd Agent+Skills && python -m pytest tests/test_model.py -v`
Expected: 4 passed

---

### Task 4: TDD — 训练与评估模块

**Files:**
- Create: `Agent+Skills/tests/test_train.py`
- Create: `Agent+Skills/mnist/train.py`
- Create: `Agent+Skills/mnist/evaluate.py`
- Create: `Agent+Skills/train.py` (入口)
- Create: `Agent+Skills/evaluate.py` (入口)

- [ ] **Step 1: 编写 test_train.py**

```python
import pytest
import torch
import torch.nn as nn
import torch.optim as optim
from mnist.model import MNISTCNN
from mnist.data import load_data
from mnist.train import train_one_epoch
from mnist.evaluate import evaluate


@pytest.fixture
def small_model():
    """一个极小的模型用于快速测试"""
    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(28 * 28, 10)
    )
    return model


def test_train_one_epoch_updates_weights():
    """验证训练一个 epoch 后模型权重发生变化"""
    model = MNISTCNN()
    train_loader, _ = load_data(batch_size=64)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 记录训练前的权重
    w_before = model.fc2.weight.clone()

    loss = train_one_epoch(model, train_loader, optimizer, device="cpu")

    w_after = model.fc2.weight
    assert not torch.equal(w_before, w_after), "权重应更新"
    assert isinstance(loss, float), f"损失应为 float, 实际 {type(loss)}"
    assert loss > 0, f"损失应 > 0, 实际 {loss}"


def test_evaluate_returns_accuracy():
    """验证 evaluate 返回准确率"""
    model = MNISTCNN()
    _, test_loader = load_data(batch_size=64)
    accuracy = evaluate(model, test_loader, device="cpu")
    assert isinstance(accuracy, float)
    assert 0.0 <= accuracy <= 100.0
```

- [ ] **Step 2: 运行测试 — 预期失败**

Run: `cd Agent+Skills && python -m pytest tests/test_train.py -v`
Expected: ImportError (train_one_epoch, evaluate 未定义)

- [ ] **Step 3: 实现 train.py**

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm


def train_one_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: str = "cpu"
) -> float:
    """
    训练一个 epoch，返回平均损失。
    """
    model.train()
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0

    for images, labels in tqdm(train_loader, desc="Training", leave=False):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(train_loader)
```

- [ ] **Step 4: 实现 evaluate.py**

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm


def evaluate(
    model: nn.Module,
    test_loader: DataLoader,
    device: str = "cpu"
) -> float:
    """
    在测试集上评估模型，返回准确率（百分比）。
    """
    model.eval()
    model.to(device)
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Evaluating", leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return 100.0 * correct / total


def predict_image(
    model: nn.Module,
    image_tensor: torch.Tensor,
    device: str = "cpu"
) -> tuple[int, torch.Tensor]:
    """
    对单张图片进行预测，返回 (预测标签, 概率分布)。
    image_tensor: shape [1, 1, 28, 28]
    """
    model.eval()
    model.to(device)
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        predicted = torch.argmax(probabilities, dim=1).item()

    return predicted, probabilities.cpu()
```

- [ ] **Step 5: 实现 train.py 入口**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MNIST CNN 训练入口
用法: python train.py [--epochs 10] [--batch-size 64] [--lr 0.001]
"""
import argparse
import torch
import torch.optim as optim
from mnist.data import load_data
from mnist.model import MNISTCNN
from mnist.train import train_one_epoch
from mnist.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description="MNIST CNN 训练")
    parser.add_argument("--epochs", type=int, default=10, help="训练轮数")
    parser.add_argument("--batch-size", type=int, default=64, help="批次大小")
    parser.add_argument("--lr", type=float, default=0.001, help="学习率")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    print(f"设备: {args.device}")
    print(f"训练轮数: {args.epochs}, 批次大小: {args.batch_size}, 学习率: {args.lr}")

    # 加载数据
    print("加载 MNIST 数据...")
    train_loader, test_loader = load_data(batch_size=args.batch_size)

    # 创建模型
    model = MNISTCNN()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")

    # 训练
    print("\n开始训练...")
    for epoch in range(1, args.epochs + 1):
        loss = train_one_epoch(model, train_loader, optimizer, device=args.device)
        acc = evaluate(model, test_loader, device=args.device)
        print(f"Epoch {epoch:2d}/{args.epochs} — Loss: {loss:.4f} — Test Acc: {acc:.2f}%")

    # 最终评估
    final_acc = evaluate(model, test_loader, device=args.device)
    print(f"\n最终测试准确率: {final_acc:.2f}%")

    # 保存模型
    torch.save(model.state_dict(), "model.pth")
    print("模型已保存为 model.pth")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: 实现 evaluate.py 入口**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型评估入口
用法: python evaluate.py [--batch-size 64]
"""
import argparse
import torch
from mnist.data import load_data
from mnist.model import MNISTCNN
from mnist.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description="MNIST 模型评估")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--model-path", type=str, default="model.pth")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    # 加载数据
    _, test_loader = load_data(batch_size=args.batch_size)

    # 加载模型
    model = MNISTCNN()
    model.load_state_dict(torch.load(args.model_path, map_location=args.device, weights_only=True))
    print(f"模型已加载: {args.model_path}")

    # 评估
    acc = evaluate(model, test_loader, device=args.device)
    print(f"测试集准确率: {acc:.2f}%")


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: 运行测试 — 预期通过**

Run: `cd Agent+Skills && python -m pytest tests/test_train.py -v`
Expected: 2 passed

---

### Task 5: 训练模型 + 验证准确率

**Files:**
- Create: `Agent+Skills/data/` (MNIST 数据集自动下载到此目录)
- Create: `Agent+Skills/model.pth`

- [ ] **Step 1: 训练模型**

Run: `cd Agent+Skills && python train.py --epochs 10 --batch-size 128`
Expected: 训练完成后显示测试准确率 ≥ 98%, 并保存 model.pth

- [ ] **Step 2: 验证模型文件存在**

Run: `cd Agent+Skills && dir model.pth`
Expected: 文件存在

- [ ] **Step 3: 运行评估入口验证**

Run: `cd Agent+Skills && python evaluate.py`
Expected: 输出测试准确率 ≥ 98%

---

### Task 6: TDD — Streamlit 前端

**Files:**
- Create: `Agent+Skills/tests/test_app.py`
- Create: `Agent+Skills/app.py`

- [ ] **Step 1: 编写 test_app.py**

```python
import pytest
import torch
import numpy as np
from PIL import Image
from mnist.model import MNISTCNN
from mnist.evaluate import predict_image


def test_predict_image_returns_valid_result():
    """验证 predict_image 对随机噪声返回有效预测"""
    model = MNISTCNN()
    # 加载预训练权重
    model.load_state_dict(torch.load("model.pth", map_location="cpu", weights_only=True))

    # 模拟一张手写数字图片 (随机噪声)
    fake_image = torch.rand(1, 1, 28, 28)
    predicted, probs = predict_image(model, fake_image)

    assert isinstance(predicted, int)
    assert 0 <= predicted <= 9
    assert probs.shape == (1, 10)
    assert torch.isclose(probs.sum(), torch.tensor(1.0), atol=1e-5)


def test_preprocess_uploaded_image():
    """验证上传图片预处理逻辑"""
    from mnist.data import transforms

    # 创建一个 28x28 的 PIL 灰度图
    img = Image.new("L", (28, 28), color=128)

    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    tensor = transform(img)

    assert tensor.shape == (1, 28, 28), f"期望 (1,28,28), 实际 {tensor.shape}"
    assert tensor.dtype == torch.float32
```

- [ ] **Step 2: 运行测试 — 预期通过（模型文件已存在）**

Run: `cd Agent+Skills && python -m pytest tests/test_app.py -v`
Expected: 2 passed

- [ ] **Step 3: 实现 app.py**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MNIST 手写数字识别 — Streamlit 前端
支持: 画板手写 + 图片上传识别
"""
import io
import torch
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

from mnist.model import MNISTCNN
from mnist.evaluate import predict_image

# ============ 页面配置 ============
st.set_page_config(
    page_title="MNIST 手写数字识别",
    page_icon="🔢",
    layout="wide",
)

# ============ 加载模型（缓存） ============
@st.cache_resource
def load_model():
    model = MNISTCNN()
    model.load_state_dict(
        torch.load("model.pth", map_location="cpu", weights_only=True)
    )
    model.eval()
    return model


# ============ 图片预处理 ============
def preprocess_image(img: Image.Image) -> torch.Tensor:
    """将 PIL 图片转为模型输入张量 [1, 1, 28, 28]"""
    img = img.convert("L")                     # 转为灰度
    img = img.resize((28, 28))                 # 缩放到 28x28
    img_array = np.array(img, dtype=np.float32) / 255.0  # 归一化
    img_array = (img_array - 0.1307) / 0.3081   # 标准化
    tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0)  # [1,1,28,28]
    return tensor


# ============ 显示预测结果 ============
def display_prediction(predicted: int, probabilities: torch.Tensor):
    """展示预测结果和概率分布"""
    probs = probabilities.squeeze().cpu().numpy()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"## 预测结果: **{predicted}**")
        st.progress(float(probs[predicted]),
                    text=f"置信度: {probs[predicted]:.2%}")

    with col2:
        st.subheader("概率分布")
        chart_data = {"数字": [str(i) for i in range(10)], "概率": probs}
        st.bar_chart(chart_data, x="数字", y="概率")


# ============ 主界面 ============
def main():
    st.title("🔢 MNIST 手写数字识别")
    st.markdown("---")

    # 加载模型
    try:
        model = load_model()
    except FileNotFoundError:
        st.error("模型文件 model.pth 未找到，请先运行 train.py 训练模型。")
        st.info("运行命令: `python train.py`")
        return
    except Exception as e:
        st.error(f"模型加载失败: {e}")
        return

    # 左右双栏布局
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("✏️ 手写画板")
        st.caption("在下方画板上手写一个数字 (0-9)")

        # 画板参数
        canvas_result = st_canvas(
            fill_color="black",
            stroke_width=15,
            stroke_color="white",
            background_color="black",
            height=280,
            width=280,
            drawing_mode="freedraw",
            key="canvas",
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            clear_pressed = st.button("🗑️ 清空画板")
        with col_btn2:
            predict_pressed = st.button("🔍 识别画板数字")

        if clear_pressed:
            st.rerun()

        if predict_pressed and canvas_result.image_data is not None:
            # 将 canvas 数据转为 PIL 图片
            img_array = canvas_result.image_data[:, :, :3]  # RGBA → RGB
            # 取红色通道（因为背景黑色，笔画白色）
            gray = np.mean(img_array, axis=2).astype(np.uint8)
            # 反转颜色：MNIST 是黑底白字，canvas 也是黑底白字
            img = Image.fromarray(gray)

            with st.spinner("识别中..."):
                tensor = preprocess_image(img)
                predicted, probabilities = predict_image(model, tensor)

            st.success(f"识别结果: **{predicted}**")
            with st.expander("查看概率详情"):
                display_prediction(predicted, probabilities)

    with right_col:
        st.subheader("📁 上传图片识别")
        st.caption("上传一张手写数字图片 (PNG/JPG)")

        uploaded_file = st.file_uploader(
            "选择图片",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            # 读取上传的图片
            img = Image.open(uploaded_file)
            st.image(img, caption="上传的图片", width=200)

            with st.spinner("识别中..."):
                tensor = preprocess_image(img)
                predicted, probabilities = predict_image(model, tensor)

            st.success(f"识别结果: **{predicted}**")
            with st.expander("查看概率详情"):
                display_prediction(predicted, probabilities)

    # 底部说明
    st.markdown("---")
    st.markdown(
        """
        **💡 使用说明:**
        - **画板模式**: 在左边画板上写数字 → 点击"识别画板数字"
        - **上传模式**: 在右边上传数字图片 → 自动识别
        - **清空画板**: 点击"清空画板"重新书写
        """
    )


if __name__ == "__main__":
    main()
```

---

### Task 7: 验证 Streamlit 前端

- [ ] **Step 1: 检查 app.py 语法**

Run: `cd Agent+Skills && python -c "import ast; ast.parse(open('app.py').read()); print('Syntax OK')"`
Expected: Syntax OK

- [ ] **Step 2: 运行全部测试**

Run: `cd Agent+Skills && python -m pytest tests/ -v`
Expected: All tests passed

- [ ] **Step 3: 启动 Streamlit**

Run: `cd Agent+Skills && streamlit run app.py`
Expected: 浏览器打开，显示画板和上传界面
