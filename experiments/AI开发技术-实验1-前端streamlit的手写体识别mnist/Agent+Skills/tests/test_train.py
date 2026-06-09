import pytest
import torch
import torch.optim as optim
from mnist.model import MNISTCNN
from mnist.data import load_data
from mnist.train import train_one_epoch
from mnist.evaluate import evaluate


def test_train_one_epoch_updates_weights():
    """验证训练一个 epoch 后模型权重发生变化"""
    model = MNISTCNN()
    train_loader, _ = load_data(batch_size=64)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    w_before = model.fc2.weight.clone()
    loss = train_one_epoch(model, train_loader, optimizer, device="cpu")
    w_after = model.fc2.weight

    assert not torch.equal(w_before, w_after), "权重应更新"
    assert isinstance(loss, float)
    assert loss > 0


def test_evaluate_returns_accuracy():
    """验证 evaluate 返回准确率"""
    model = MNISTCNN()
    _, test_loader = load_data(batch_size=64)
    accuracy = evaluate(model, test_loader, device="cpu")
    assert isinstance(accuracy, float)
    assert 0.0 <= accuracy <= 100.0
