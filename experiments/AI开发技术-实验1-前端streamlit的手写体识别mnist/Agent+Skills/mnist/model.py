"""MNIST CNN 模型定义"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MNISTCNN(nn.Module):
    """卷积神经网络用于 MNIST 手写数字识别"""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=0)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=0)
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
