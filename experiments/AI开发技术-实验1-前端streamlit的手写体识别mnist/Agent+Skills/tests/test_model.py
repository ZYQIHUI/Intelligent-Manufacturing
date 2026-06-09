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
    assert torch.allclose(output.sum(dim=1), torch.ones(8), atol=1e-5)


def test_model_parameter_count():
    """验证模型有合理的参数量（>10万 <1千万）"""
    model = MNISTCNN()
    total_params = sum(p.numel() for p in model.parameters())
    assert total_params > 100_000, f"参数量 {total_params} 太小"
    assert total_params < 10_000_000, f"参数量 {total_params} 太大"
