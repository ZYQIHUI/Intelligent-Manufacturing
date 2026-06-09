"""MNIST 数据加载模块"""
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def load_data(batch_size: int = 64) -> tuple[DataLoader, DataLoader]:
    """加载 MNIST 数据集，返回 (train_loader, test_loader)"""
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    train_dataset = datasets.MNIST(
        root="./data", train=True, download=True, transform=transform
    )
    test_dataset = datasets.MNIST(
        root="./data", train=False, download=False, transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader
