"""训练模块"""
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
    """训练一个 epoch，返回平均损失"""
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
