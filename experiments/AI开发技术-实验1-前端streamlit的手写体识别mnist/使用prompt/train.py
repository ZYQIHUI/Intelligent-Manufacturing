# -*- coding: utf-8 -*-
"""
手写数字识别（MNIST）—— CNN 训练脚本
======================================
功能：加载 MNIST 数据集，构建卷积神经网络进行训练，
      保存模型为 mnist_model.h5，并打印每个 epoch 的准确率。
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, utils, datasets

# -------------------- 1. 加载 MNIST 数据集 --------------------
print("正在加载 MNIST 数据集 ...")
(x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()

print(f"训练集形状: {x_train.shape}, 测试集形状: {x_test.shape}")

# -------------------- 2. 数据预处理 --------------------

# 2.1 归一化：将像素值从 [0, 255] 缩放到 [0, 1]
x_train = x_train.astype("float32") / 255.0
x_test  = x_test.astype("float32") / 255.0

# 2.2 调整形状：从 (28, 28) 变为 (28, 28, 1)，增加通道维度
x_train = x_train.reshape(-1, 28, 28, 1)
x_test  = x_test.reshape(-1, 28, 28, 1)

# 2.3 标签独热编码：将数字标签（0-9）转为 10 维 one-hot 向量
y_train = utils.to_categorical(y_train, num_classes=10)
y_test  = utils.to_categorical(y_test,  num_classes=10)

print("数据预处理完成。")

# -------------------- 3. 构建 CNN 模型 --------------------
model = keras.Sequential([
    # 第一卷积块：Conv2D + ReLU + MaxPooling
    layers.Conv2D(
        filters=32,                 # 32 个卷积核
        kernel_size=(3, 3),         # 卷积核大小 3x3
        activation="relu",          # ReLU 激活函数
        input_shape=(28, 28, 1)     # 输入形状：28x28 灰度图
    ),
    layers.MaxPooling2D(pool_size=(2, 2)),  # 2x2 最大池化，降低特征图尺寸

    # 第二卷积块：Conv2D + ReLU + MaxPooling
    layers.Conv2D(
        filters=64,                 # 64 个卷积核
        kernel_size=(3, 3),         # 卷积核大小 3x3
        activation="relu"           # ReLU 激活函数
    ),
    layers.MaxPooling2D(pool_size=(2, 2)),  # 2x2 最大池化

    # 展平层：将二维特征图转为一维向量
    layers.Flatten(),

    # 全连接层：128 个神经元 + ReLU 激活
    layers.Dense(128, activation="relu"),

    # Dropout 层：随机丢弃 50% 的神经元，防止过拟合
    layers.Dropout(0.5),

    # 输出层：10 个神经元（对应 0-9 十个数字），softmax 输出概率分布
    layers.Dense(10, activation="softmax")
])

# 打印模型结构总览
model.summary()

# -------------------- 4. 编译模型 --------------------
model.compile(
    optimizer="adam",                         # Adam 优化器，自适应学习率
    loss="categorical_crossentropy",          # 多分类交叉熵损失函数
    metrics=["accuracy"]                      # 评估指标：准确率
)

# -------------------- 5. 训练模型 --------------------
print("\n开始训练 ...")
history = model.fit(
    x_train, y_train,                         # 训练数据及标签
    batch_size=128,                           # 每批 128 个样本
    epochs=10,                                # 训练 10 轮
    validation_split=0.1,                     # 从训练集中划分 10% 作为验证集
    verbose=1                                 # 打印详细日志（含每个 epoch 的准确率）
)

# -------------------- 6. 评估模型 --------------------
print("\n在测试集上评估 ...")
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"测试集损失: {test_loss:.4f}")
print(f"测试集准确率: {test_acc:.4f}")

# -------------------- 7. 保存模型 --------------------
model.save("mnist_model.h5")
print("\n模型已保存为 mnist_model.h5")

# -------------------- 8. 绘制训练曲线（可选） --------------------
try:
    import matplotlib.pyplot as plt
    import matplotlib

    # 解决 matplotlib 中文乱码：设置中文字体
    # Windows 环境下使用 SimHei（黑体），macOS 使用 Heiti TC / Arial Unicode MS
    matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei",
                                               "WenQuanYi Micro Hei", "Arial Unicode MS"]
    matplotlib.rcParams["axes.unicode_minus"] = False  # 解决负号显示异常

    # 绘制训练 & 验证准确率曲线
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history.history["accuracy"], label="训练准确率")
    plt.plot(history.history["val_accuracy"], label="验证准确率")
    plt.title("准确率曲线")
    plt.xlabel("Epoch")
    plt.ylabel("准确率")
    plt.legend()

    # 绘制训练 & 验证损失曲线
    plt.subplot(1, 2, 2)
    plt.plot(history.history["loss"], label="训练损失")
    plt.plot(history.history["val_loss"], label="验证损失")
    plt.title("损失曲线")
    plt.xlabel("Epoch")
    plt.ylabel("损失值")
    plt.legend()

    plt.tight_layout()
    plt.savefig("training_curves.png", dpi=150)
    print("训练曲线图已保存为 training_curves.png")
except ImportError:
    print("未安装 matplotlib，跳过绘制训练曲线。")
except Exception as e:
    print(f"绘制训练曲线时出错: {e}")
