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
