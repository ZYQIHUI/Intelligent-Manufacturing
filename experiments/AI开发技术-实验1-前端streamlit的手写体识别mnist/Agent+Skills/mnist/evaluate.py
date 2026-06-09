"""评估与预测模块"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm


def evaluate(
    model: nn.Module,
    test_loader: DataLoader,
    device: str = "cpu"
) -> float:
    """在测试集上评估模型，返回准确率（百分比）"""
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
    """对单张图片进行预测，返回 (预测标签, 概率分布)"""
    model.eval()
    model.to(device)
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        predicted = torch.argmax(probabilities, dim=1).item()

    return predicted, probabilities.cpu()
